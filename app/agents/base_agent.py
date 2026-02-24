"""Abstract base class for all LangChain agents in langchain-poc."""

from abc import ABC, abstractmethod
from typing import Any

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class providing common structure for all agents.

    Subclasses must implement :meth:`build_executor` if they need custom
    executor configuration, and should expose domain-specific public methods.

    Args:
        name: Logical agent name used in logging.
        model: OpenAI model identifier (e.g. ``"gpt-4o"``).
        tools: List of LangChain tools available to the agent.
        system_prompt: System-level instruction for the LLM.
    """

    def __init__(
        self,
        name: str,
        model: str,
        tools: list[BaseTool],
        system_prompt: str,
    ) -> None:
        self.name = name
        self.model = model
        self.tools = tools
        self.system_prompt = system_prompt
        self._llm = ChatOpenAI(model=model, temperature=0)
        self._executor: AgentExecutor | None = None

    def build_executor(self) -> AgentExecutor:
        """Construct and return a LangChain AgentExecutor.

        Returns:
            AgentExecutor: Ready-to-use executor with the configured tools.
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        agent = create_openai_tools_agent(self._llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=False)

    @property
    def executor(self) -> AgentExecutor:
        """Lazily build and cache the AgentExecutor.

        Returns:
            AgentExecutor: The agent executor instance.
        """
        if self._executor is None:
            self._executor = self.build_executor()
        return self._executor

    def invoke(self, input: str, session_id: str | None = None) -> str:  # noqa: A002
        """Invoke the agent with a plain-text input.

        Args:
            input: User message or instruction.
            session_id: Optional session identifier (used by stateful agents).

        Returns:
            str: The agent's textual response.
        """
        logger.info("agent_invoke", agent=self.name, session_id=session_id)
        result: Any = self.executor.invoke({"input": input})
        return result.get("output", "")
