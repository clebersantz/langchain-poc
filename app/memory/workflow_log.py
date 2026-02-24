"""SQLite workflow execution log."""

import json
from datetime import datetime

import sqlalchemy as sa

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_engine = sa.create_engine(settings.database_url)


def log_workflow_start(workflow_name: str, trigger: str, context: dict) -> int:
    """Insert a new workflow_log row and return the new row id.

    Args:
        workflow_name: Name of the workflow being started.
        trigger: How the workflow was triggered (``"manual"``, ``"webhook"``,
            ``"agent"``).
        context: Input context dict (will be stored as JSON).

    Returns:
        int: The id of the new log row.
    """
    with _engine.begin() as conn:
        result = conn.execute(
            sa.text(
                """
                INSERT INTO workflow_log (workflow_name, trigger, context_json, status, started_at)
                VALUES (:name, :trigger, :ctx, 'running', :now)
                """
            ),
            {
                "name": workflow_name,
                "trigger": trigger,
                "ctx": json.dumps(context),
                "now": datetime.utcnow().isoformat(),
            },
        )
        log_id = result.lastrowid
    logger.info("workflow_log_start", log_id=log_id, name=workflow_name)
    return log_id


def log_workflow_complete(log_id: int, steps: list, status: str = "success") -> None:
    """Update an existing workflow_log row with completion data.

    Args:
        log_id: The row id returned by :func:`log_workflow_start`.
        steps: List of executed step names.
        status: Final status string (``"success"`` or ``"failed"``).
    """
    with _engine.begin() as conn:
        conn.execute(
            sa.text(
                """
                UPDATE workflow_log
                SET status = :status, steps_json = :steps, completed_at = :now
                WHERE id = :id
                """
            ),
            {
                "status": status,
                "steps": json.dumps(steps),
                "now": datetime.utcnow().isoformat(),
                "id": log_id,
            },
        )
    logger.info("workflow_log_complete", log_id=log_id, status=status)


def get_workflow_history(
    workflow_name: str | None = None, limit: int = 20
) -> list[dict]:
    """Query the workflow log.

    Args:
        workflow_name: Filter to a specific workflow, or None for all.
        limit: Maximum number of rows to return.

    Returns:
        list[dict]: Log rows as dictionaries.
    """
    with _engine.connect() as conn:
        if workflow_name:
            rows = conn.execute(
                sa.text(
                    "SELECT * FROM workflow_log WHERE workflow_name = :name "
                    "ORDER BY started_at DESC LIMIT :limit"
                ),
                {"name": workflow_name, "limit": limit},
            )
        else:
            rows = conn.execute(
                sa.text(
                    "SELECT * FROM workflow_log ORDER BY started_at DESC LIMIT :limit"
                ),
                {"limit": limit},
            )
        return [dict(row._mapping) for row in rows]
