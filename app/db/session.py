from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


settings = get_settings()
database_url = settings.normalized_database_url
engine_kwargs = {"future": True}
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def init_db():
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _run_lightweight_migrations()


def _run_lightweight_migrations():
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with engine.begin() as connection:
        if "users" in tables:
            user_columns = {column["name"] for column in inspector.get_columns("users")}
            if "is_admin" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0"))

        if "audit_logs" not in tables:
            from app.db.models import AuditLog

            AuditLog.__table__.create(bind=connection, checkfirst=True)
