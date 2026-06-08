import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.db.repository import (
    create_analysis,
    create_audit_log,
    create_user,
    ensure_admin_bootstrap,
    get_platform_metrics,
    list_analyses_for_user,
    list_recent_analyses,
    list_recent_audit_logs,
)
from app.utils.admin import is_admin_email, is_admin_user


class AdminAndAuditTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", future=True)
        TestingSession = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)
        Base.metadata.create_all(bind=self.engine)
        self.db = TestingSession()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_admin_email_bootstrap_is_applied_on_user_creation(self):
        user = create_user(self.db, "mrmoeve@gmail.com", "hashed")
        self.assertEqual(user.is_admin, 1)
        self.assertTrue(is_admin_user(user))
        self.assertTrue(is_admin_email(user.email))

    def test_existing_admin_email_user_is_upgraded_by_bootstrap(self):
        user = create_user(self.db, "analyst@example.com", "hashed")
        user.email = "mrmoeve@gmail.com"
        user.is_admin = 0
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        updated = ensure_admin_bootstrap(self.db, user)
        self.assertEqual(updated.is_admin, 1)

    def test_audit_log_persists_required_actions(self):
        user = create_user(self.db, "user@example.com", "hashed")
        create_audit_log(self.db, "login", user.email, "auth", "login", user.id)
        create_audit_log(self.db, "signup", user.email, "auth", "signup", user.id)
        logs = list_recent_audit_logs(self.db)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["action"], "signup")
        self.assertEqual(logs[1]["action"], "login")

    def test_platform_metrics_include_users_analyses_and_audit_events(self):
        user = create_user(self.db, "user@example.com", "hashed")
        create_analysis(
            self.db,
            user_id=user.id,
            company_name="Example Co",
            document_name="example-10k.pdf",
            document_type="10-K",
            extracted_text="Revenue improved.",
            analysis_json={"financial_health_score": 82},
            financial_health_score=82,
        )
        create_audit_log(self.db, "analysis_generation", user.email, "analysis", "example-10k.pdf", user.id)

        metrics = get_platform_metrics(self.db)
        self.assertEqual(metrics["total_users"], 1)
        self.assertEqual(metrics["total_analyses"], 1)
        self.assertEqual(metrics["total_audit_events"], 1)
        self.assertEqual(metrics["average_health_score"], 82.0)

    def test_analysis_persistence_returns_serialized_dto_safe_after_session_close(self):
        user = create_user(self.db, "user@example.com", "hashed")
        saved = create_analysis(
            self.db,
            user_id=user.id,
            company_name="Tesla",
            document_name="tesla-10k.pdf",
            document_type="10-K",
            extracted_text="Revenue improved.",
            analysis_json={"financial_health_score": 75, "executive_summary": "Stable."},
            financial_health_score=75,
        )
        self.db.close()

        self.assertEqual(saved["company_name"], "Tesla")
        self.assertEqual(saved["document_name"], "tesla-10k.pdf")
        self.assertEqual(saved["financial_health_score"], 75)
        self.assertEqual(saved["analysis_json"]["executive_summary"], "Stable.")

    def test_analysis_history_retrieval_returns_serialized_records(self):
        user = create_user(self.db, "user@example.com", "hashed")
        create_analysis(
            self.db,
            user_id=user.id,
            company_name="First Co",
            document_name="first.pdf",
            document_type="10-Q",
            extracted_text="First text",
            analysis_json={"financial_health_score": 70},
            financial_health_score=70,
        )
        create_analysis(
            self.db,
            user_id=user.id,
            company_name="Second Co",
            document_name="second.pdf",
            document_type="10-K",
            extracted_text="Second text",
            analysis_json={"financial_health_score": 88},
            financial_health_score=88,
        )

        history = list_analyses_for_user(self.db, user.id)
        recent = list_recent_analyses(self.db, limit=10)
        self.db.close()

        self.assertEqual(history[0]["company_name"], "Second Co")
        self.assertEqual(history[1]["company_name"], "First Co")
        self.assertEqual(recent[0]["document_name"], "second.pdf")
        self.assertEqual(recent[1]["document_name"], "first.pdf")


if __name__ == "__main__":
    unittest.main()
