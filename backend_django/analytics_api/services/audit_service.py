from django.utils import timezone
from ..models import AuditLog


def log_audit_action(actor_type, actor_name, entity_type, entity_id, action, changes="", ip_address="127.0.0.1", actor_id=None, session_id=None):
    """
    Creates an immutable WORM audit log entry in the SQL database.
    """
    try:
        return AuditLog.objects.create(
            actor_id=actor_id,
            actor_type=actor_type,
            actor_name=actor_name,
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            changes=str(changes),
            ip_address=ip_address,
            session_id=session_id,
            created_at=timezone.now()
        )
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to record audit log: {e}")
        return None
