from app.db import repository


def log_event(
    db_session,
    action: str,
    user_email: str,
    target_type: str,
    target_name: str = "",
    user_id: str | None = None,
    metadata_json: dict | None = None,
):
    try:
        repository.create_audit_log(
            db_session=db_session,
            action=action,
            user_email=user_email,
            target_type=target_type,
            target_name=target_name,
            user_id=user_id,
            metadata_json=metadata_json,
        )
    except Exception:
        return None
    return True
