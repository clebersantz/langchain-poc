"""Chat API route — POST /chat."""

from fastapi import APIRouter

from app.agents.supervisor import SupervisorAgent
from app.api.schemas import ChatRequest, ChatResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

_supervisor: SupervisorAgent | None = None


def _get_supervisor() -> SupervisorAgent:
    """Return a lazily initialized SupervisorAgent instance."""
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a user chat message and return the agent's response.

    Routes the message through the Supervisor Agent which determines intent
    and delegates to the appropriate sub-agent.

    Args:
        request: Chat request containing ``session_id`` and ``message``.

    Returns:
        ChatResponse: The response with ``session_id``, ``response``, and
            ``agent_used``.
    """
    logger.info("chat_request", session_id=request.session_id)
    response, agent_used = _get_supervisor().route(request.message, request.session_id)
    return ChatResponse(
        session_id=request.session_id,
        response=response,
        agent_used=agent_used,
    )
