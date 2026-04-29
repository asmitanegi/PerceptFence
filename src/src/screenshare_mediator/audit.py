"""Audit logger for policy and output-guard decisions.

The logger records decision metadata only. It does not claim tamper evidence and
it does not store raw screen, speech, notification, model-context, or assistant
output content.
"""

from __future__ import annotations

from .models import OutputGuardDecision, PolicyDecision


class AuditLogger:
    """Collect decision metadata for the smoke path."""

    def __init__(self) -> None:
        self._events: list[dict[str, str]] = []

    @property
    def events(self) -> tuple[dict[str, str], ...]:
        return tuple(dict(event) for event in self._events)

    def record(self, decision: PolicyDecision) -> dict[str, str]:
        event = {
            "event_type": "policy_decision",
            "fixture_id": decision.fixture_id,
            "scenario_class": decision.scenario_class,
            "action": decision.action,
            "reason": decision.reason,
        }
        self._events.append(event)
        return event

    def record_context_exclusion(self, decision: PolicyDecision) -> dict[str, str]:
        event = {
            "event_type": "context_exclusion",
            "fixture_id": decision.fixture_id,
            "scenario_class": decision.scenario_class,
            "action": "exclude_before_assistant_context",
            "reason": f"excluded before assistant context: {decision.action}",
        }
        self._events.append(event)
        return event

    def record_output_guard(self, decision: OutputGuardDecision) -> dict[str, str]:
        event = {
            "event_type": "output_guard_decision",
            "fixture_id": decision.fixture_id,
            "scenario_class": decision.scenario_class,
            "action": decision.action,
            "reason": decision.reason,
            "allowed": str(decision.allowed).lower(),
        }
        self._events.append(event)
        return event
