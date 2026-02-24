"""SQLite-backed session memory for conversation history."""

from langchain_community.chat_message_histories import SQLChatMessageHistory

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def init_db() -> None:
    """Ensure all required SQLite tables exist.

    Creates the ``chat_history`` table (managed by LangChain) and the
    ``workflow_log`` table used for workflow audit logging.
    """
    import sqlalchemy as sa

    engine = sa.create_engine(settings.database_url)
    with engine.begin() as conn:
        conn.execute(
            sa.text(
                """
                CREATE TABLE IF NOT EXISTS workflow_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_name TEXT NOT NULL,
                    trigger TEXT NOT NULL DEFAULT 'manual',
                    context_json TEXT,
                    status TEXT NOT NULL DEFAULT 'running',
                    steps_json TEXT,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                )
                """
            )
        )
    logger.info("db_init_complete")


def get_session_history(session_id: str) -> SQLChatMessageHistory:
    """Return (or create) the message history for a conversation session.

    Args:
        session_id: Unique identifier for the conversation session.

    Returns:
        SQLChatMessageHistory: LangChain message history backed by SQLite.
    """
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string=settings.database_url,
    )
