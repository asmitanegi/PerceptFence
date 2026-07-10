"""Session memory gate for mediated model context."""

from __future__ import annotations

from dataclasses import replace

from .models import MediatedSession


class SessionMemoryGate:
    """Apply memory controls before content enters the assistant context."""

    def __init__(self) -> None:
        self._writes: list[str] = []
        self._exclusions: list[str] = []

    @property
    def writes(self) -> tuple[str, ...]:
        return tuple(self._writes)

    @property
    def exclusions(self) -> tuple[str, ...]:
        return tuple(self._exclusions)

    def exclude_from_context(self, session: MediatedSession) -> MediatedSession:
        """Remove non-retainable content before the assistant call.

        This is mode-a gating: excluded content never reaches the model context
        for this turn. It is not a prompt telling the model to ignore content and
        it is not post-hoc history deletion after the assistant has seen it.
        """
        if session.memory_allowed:
            return session
        self._exclusions.append(f"{session.fixture_id}:{session.decision.action}")
        return replace(session, model_context="")

    def maybe_write(self, session: MediatedSession) -> bool:
        if not session.memory_allowed:
            return False
        self._writes.append(f"{session.fixture_id}:{session.decision.action}")
        return True
