"""Small data contracts for the synthetic runtime mediation path."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CapturedSession:
    """Normalized synthetic session content before policy mediation."""

    fixture_id: str
    scenario_class: str
    modalities: tuple[str, ...]
    window_title: str | None
    screen_text: str
    speech_transcript: str
    notification_text: str
    events: tuple[dict[str, Any], ...] = ()
    layout: dict[str, Any] = field(default_factory=dict)

    @property
    def raw_context(self) -> str:
        """Return the raw context a baseline assistant would receive."""
        chunks = [
            self.window_title or "",
            self.screen_text,
            self.notification_text,
            self.speech_transcript,
        ]
        for event in self.events:
            chunks.append(str(event.get("window_title", "")))
            chunks.append(str(event.get("visible_text", "")))
        return "\n".join(chunk for chunk in chunks if chunk)


@dataclass(frozen=True)
class PolicyDecision:
    """Policy action selected for a captured synthetic session."""

    fixture_id: str
    scenario_class: str
    action: str
    reason: str


@dataclass(frozen=True)
class MediatedSession:
    """Session content after mediation and before model use."""

    fixture_id: str
    scenario_class: str
    model_context: str
    decision: PolicyDecision
    memory_allowed: bool


@dataclass(frozen=True)
class OutputGuardContext:
    """Policy-only context for the output guard.

    This is intentionally separate from the assistant model context: it contains
    only policy metadata and never includes raw screen text, speech,
    notification text, or the mediated assistant context.
    """

    fixture_id: str
    scenario_class: str
    policy_action: str
    policy_reason: str
    blocked_categories: tuple[str, ...] = ()


@dataclass(frozen=True)
class OutputGuardDecision:
    """Output guard verdict for one assistant candidate response."""

    fixture_id: str
    scenario_class: str
    action: str
    reason: str
    allowed: bool
    replacement: str | None = None


@dataclass(frozen=True)
class RuntimeResult:
    """Observable result for either the baseline or guarded smoke path."""

    path: str
    fixture_id: str
    model_context: str
    assistant_output: str
    memory_writes: tuple[str, ...]
    audit_events: tuple[dict[str, str], ...]
