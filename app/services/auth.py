from passlib.context import CryptContext

from app.db import repository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def register_user(db_session, email: str, password: str):
    existing_user = repository.get_user_by_email(db_session, email)
    if existing_user:
        raise ValueError("An account with this email already exists.")
    return repository.create_user(db_session, email, hash_password(password))


def authenticate_user(db_session, email: str, password: str):
    user = repository.get_user_by_email(db_session, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
