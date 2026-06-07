from passlib.context import CryptContext

from app.db import repository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64


class PasswordValidationError(ValueError):
    pass


class PasswordHashingError(ValueError):
    pass


def normalize_password(password: str) -> str:
    return (password or "").strip()


def validate_password(password: str) -> str:
    normalized = normalize_password(password)
    if len(normalized) < PASSWORD_MIN_LENGTH:
        raise PasswordValidationError("Password must be at least 8 characters.")
    if len(normalized) > PASSWORD_MAX_LENGTH:
        raise PasswordValidationError("Password cannot exceed 64 characters.")
    return normalized


def hash_password(password: str) -> str:
    normalized = validate_password(password)
    try:
        return pwd_context.hash(normalized)
    except Exception as exc:
        raise PasswordHashingError("Unable to create account. Please use a shorter password.") from exc


def verify_password(password: str, password_hash: str) -> bool:
    normalized = validate_password(password)
    try:
        return pwd_context.verify(normalized, password_hash)
    except Exception:
        return False


def validate_password_for_reset(password: str) -> str:
    return validate_password(password)


def register_user(db_session, email: str, password: str):
    existing_user = repository.get_user_by_email(db_session, email)
    if existing_user:
        raise ValueError("An account with this email already exists.")
    try:
        return repository.create_user(db_session, email, hash_password(password))
    except PasswordHashingError:
        raise
    except Exception as exc:
        raise ValueError("Unable to create account. Please use a shorter password.") from exc


def authenticate_user(db_session, email: str, password: str):
    try:
        normalized_password = validate_password(password)
    except PasswordValidationError:
        return None
    user = repository.get_user_by_email(db_session, email)
    if not user or not verify_password(normalized_password, user.password_hash):
        return None
    return user
