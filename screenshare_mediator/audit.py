"""Audit logger for policy and output-guard decisions.

The logger records decision metadata only. It does not store raw screen,
speech, notification, model-context, or assistant-output content. Each event
carries a SHA-256 hash chained from the previous event, so an in-process
crash that truncates the log or a post-hoc edit that changes a recorded
field is detectable by replaying the chain. The chain is *crash-evident*,
not *tamper-proof* against an attacker with code-execution access on the
host: an attacker who can run new logger code can re-chain any forgery.
The threat model documents the assumption explicitly (TA7).
"""

from __future__ import annotations

import hashlib
import json

from .models import OutputGuardDecision, PolicyDecision

GENESIS_HASH = "0" * 64


class AuditLogger:
    """Collect decision metadata with a SHA-256 hash chain."""

    def __init__(self) -> None:
        self._events: list[dict[str, str]] = []
        self._last_hash: str = GENESIS_HASH

    @property
    def events(self) -> tuple[dict[str, str], ...]:
        return tuple(dict(event) for event in self._events)

    def record(self, decision: PolicyDecision) -> dict[str, str]:
        return self._append({
            "event_type": "policy_decision",
            "fixture_id": decision.fixture_id,
            "scenario_class": decision.scenario_class,
            "action": decision.action,
            "reason": decision.reason,
        })

    def record_context_exclusion(self, decision: PolicyDecision) -> dict[str, str]:
        return self._append({
            "event_type": "context_exclusion",
            "fixture_id": decision.fixture_id,
            "scenario_class": decision.scenario_class,
            "action": "exclude_before_assistant_context",
            "reason": f"excluded before assistant context: {decision.action}",
        })

    def record_output_guard(self, decision: OutputGuardDecision) -> dict[str, str]:
        return self._append({
            "event_type": "output_guard_decision",
            "fixture_id": decision.fixture_id,
            "scenario_class": decision.scenario_class,
            "action": decision.action,
            "reason": decision.reason,
            "allowed": str(decision.allowed).lower(),
        })

    def _append(self, payload: dict[str, str]) -> dict[str, str]:
        payload["prev_hash"] = self._last_hash
        digest = self._hash_event(payload)
        payload["hash"] = digest
        self._last_hash = digest
        self._events.append(payload)
        return payload

    @staticmethod
    def _hash_event(event: dict[str, str]) -> str:
        canonical = json.dumps(
            {k: v for k, v in event.items() if k != "hash"},
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def verify_chain(cls, events: tuple[dict[str, str], ...]) -> bool:
        """Return True if every event's recorded hash matches its content
        and its prev_hash chains correctly back to the genesis hash."""
        prev_hash = GENESIS_HASH
        for event in events:
            recorded = event.get("hash", "")
            recorded_prev = event.get("prev_hash", "")
            expected = cls._hash_event(event)
            if recorded != expected or recorded_prev != prev_hash:
                return False
            prev_hash = recorded
        return True
