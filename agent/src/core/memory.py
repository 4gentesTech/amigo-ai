"""Memory management for graph state persistence."""

from langgraph.checkpoint.memory import MemorySaver

from .logger import get_logger

logger = get_logger(__name__)


class MemoryHandler:
    """In-memory checkpoint handler with session management."""

    def __init__(self):
        self.checkpointer = MemorySaver()
        logger.info("Memory checkpointer initialized")

    def get_checkpointer(self) -> MemorySaver:
        """Return checkpointer instance."""
        return self.checkpointer

    def clear_session(self, thread_id: str) -> None:
        """Clear checkpoint for specific session."""
        logger.info("Session cleanup requested", session_id=thread_id)
        # TODO: Implement TTL with Redis in production


# Singleton
memory = MemoryHandler()
