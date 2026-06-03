from datetime import datetime
from app.models import db, AuditLog


def log_event(user_id, action_type, entity_type, entity_id=None, details=None):
    event = AuditLog(
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        created_at=datetime.utcnow()
    )
    db.session.add(event)
    db.session.commit()
    return event
