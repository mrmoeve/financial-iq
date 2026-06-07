from sqlalchemy import desc, select

from app.db.models import Analysis, User


def get_user_by_email(db_session, email: str) -> User | None:
    return db_session.execute(select(User).where(User.email == email.lower().strip())).scalar_one_or_none()


def create_user(db_session, email: str, password_hash: str) -> User:
    user = User(email=email.lower().strip(), password_hash=password_hash)
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
) -> Analysis:
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
    return analysis


def list_analyses_for_user(db_session, user_id) -> list[Analysis]:
    result = db_session.execute(
        select(Analysis).where(Analysis.user_id == user_id).order_by(desc(Analysis.created_at))
    )
    return list(result.scalars().all())
