from sqlalchemy import desc, func, select

from app.config import get_settings
from app.db.models import Analysis, AuditLog, User


settings = get_settings()


def _normalize_email(email: str) -> str:
    return email.lower().strip()


def is_admin_email(email: str) -> bool:
    return _normalize_email(email) == _normalize_email(settings.admin_email)


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "is_admin": bool(user.is_admin),
        "created_at": user.created_at,
    }


def serialize_analysis(analysis: Analysis) -> dict:
    return {
        "id": analysis.id,
        "user_id": analysis.user_id,
        "company_name": analysis.company_name,
        "document_name": analysis.document_name,
        "document_type": analysis.document_type,
        "extracted_text": analysis.extracted_text,
        "analysis_json": analysis.analysis_json,
        "financial_health_score": analysis.financial_health_score,
        "created_at": analysis.created_at,
    }


def serialize_audit_log(audit_log: AuditLog) -> dict:
    return {
        "id": audit_log.id,
        "user_id": audit_log.user_id,
        "user_email": audit_log.user_email,
        "action": audit_log.action,
        "target_type": audit_log.target_type,
        "target_name": audit_log.target_name,
        "metadata_json": audit_log.metadata_json,
        "created_at": audit_log.created_at,
    }


def get_user_by_email(db_session, email: str) -> User | None:
    return db_session.execute(select(User).where(User.email == _normalize_email(email))).scalar_one_or_none()


def create_user(db_session, email: str, password_hash: str) -> User:
    normalized_email = _normalize_email(email)
    user = User(email=normalized_email, password_hash=password_hash, is_admin=1 if is_admin_email(normalized_email) else 0)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def ensure_admin_bootstrap(db_session, user: User) -> User:
    if is_admin_email(user.email) and not user.is_admin:
        user.is_admin = 1
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


def create_analysis(
    db_session,
    user_id,
    company_name: str,
    document_name: str,
    document_type: str,
    extracted_text: str,
    analysis_json: dict,
    financial_health_score: int,
) -> dict:
    analysis = Analysis(
        user_id=user_id,
        company_name=company_name,
        document_name=document_name,
        document_type=document_type,
        extracted_text=extracted_text,
        analysis_json=analysis_json,
        financial_health_score=financial_health_score,
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)
    return serialize_analysis(analysis)


def list_analyses_for_user(db_session, user_id) -> list[dict]:
    result = db_session.execute(
        select(Analysis).where(Analysis.user_id == user_id).order_by(desc(Analysis.created_at))
    )
    return [serialize_analysis(item) for item in result.scalars().all()]


def create_audit_log(
    db_session,
    action: str,
    user_email: str,
    target_type: str,
    target_name: str = "",
    user_id: str | None = None,
    metadata_json: dict | None = None,
) -> dict:
    audit_log = AuditLog(
        user_id=user_id,
        user_email=_normalize_email(user_email),
        action=action,
        target_type=target_type,
        target_name=target_name,
        metadata_json=metadata_json or {},
    )
    db_session.add(audit_log)
    db_session.commit()
    db_session.refresh(audit_log)
    return serialize_audit_log(audit_log)


def list_all_users(db_session) -> list[dict]:
    result = db_session.execute(select(User).order_by(desc(User.created_at)))
    return [serialize_user(item) for item in result.scalars().all()]


def list_recent_analyses(db_session, limit: int = 100) -> list[dict]:
    result = db_session.execute(select(Analysis).order_by(desc(Analysis.created_at)).limit(limit))
    return [serialize_analysis(item) for item in result.scalars().all()]


def list_recent_audit_logs(db_session, limit: int = 200) -> list[dict]:
    result = db_session.execute(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit))
    return [serialize_audit_log(item) for item in result.scalars().all()]


def get_platform_metrics(db_session) -> dict:
    total_users = db_session.execute(select(func.count()).select_from(User)).scalar_one()
    total_analyses = db_session.execute(select(func.count()).select_from(Analysis)).scalar_one()
    total_audit_events = db_session.execute(select(func.count()).select_from(AuditLog)).scalar_one()
    avg_score = db_session.execute(select(func.avg(Analysis.financial_health_score))).scalar_one()
    return {
        "total_users": total_users or 0,
        "total_analyses": total_analyses or 0,
        "total_audit_events": total_audit_events or 0,
        "average_health_score": round(float(avg_score), 1) if avg_score is not None else None,
    }
