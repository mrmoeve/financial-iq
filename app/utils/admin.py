from app.config import get_settings
from app.db.models import User


def get_admin_email() -> str:
    return get_settings().admin_email.lower().strip()


def is_admin_email(email: str) -> bool:
    return email.lower().strip() == get_admin_email()


def is_admin_user(user: User | None) -> bool:
    if not user:
        return False
    return bool(getattr(user, "is_admin", 0)) or is_admin_email(user.email)
