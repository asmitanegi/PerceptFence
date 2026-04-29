"""Baseline and guarded runtime paths for synthetic smoke testing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .audit import AuditLogger
from .capture import SyntheticCaptureAdapter
from .memory import SessionMemoryGate
from .models import RuntimeResult
from .output_guard import OutputGuard
from .policy import ConsentPolicyEngine
from .redaction import RedactionEngine


class RuntimeMediator:
    """Run one fixture through baseline and guarded paths."""

    def __init__(self, policy_path: Path) -> None:
        self.capture_adapter = SyntheticCaptureAdapter()
        self.policy_engine = ConsentPolicyEngine.from_policy_file(policy_path)
        self.redaction_engine = RedactionEngine()
        self.output_guard = OutputGuard()

    def run_baseline(self, fixture: dict[str, Any]) -> RuntimeResult:
        captured = self.capture_adapter.capture(fixture)
        model_context = captured.raw_context
        return RuntimeResult(
            path="baseline",
            fixture_id=captured.fixture_id,
            model_context=model_context,
            assistant_output=f"Baseline observed: {model_context}",
            memory_writes=(f"{captured.fixture_id}:raw",),
            audit_events=(),
        )

    def run_guarded(self, fixture: dict[str, Any]) -> RuntimeResult:
        captured = self.capture_adapter.capture(fixture)
        decision = self.policy_engine.decide(captured)
        mediated = self.redaction_engine.mediate(captured, decision)

        memory_gate = SessionMemoryGate()
        mediated = memory_gate.exclude_from_context(mediated)
        memory_gate.maybe_write(mediated)

        audit_logger = AuditLogger()
        audit_logger.record(decision)
        if memory_gate.exclusions:
            audit_logger.record_context_exclusion(decision)

        draft_output = self._assistant_candidate_output(decision.action, mediated.model_context)
        guard_context = self.output_guard.context_from_policy(decision)
        guard_decision = self.output_guard.guard(draft_output, guard_context)
        audit_logger.record_output_guard(guard_decision)
        guarded_output = self.output_guard.apply(draft_output, guard_decision)
        return RuntimeResult(
            path="guarded",
            fixture_id=captured.fixture_id,
            model_context=mediated.model_context,
            assistant_output=guarded_output,
            memory_writes=memory_gate.writes,
            audit_events=audit_logger.events,
        )

    @staticmethod
    def _assistant_candidate_output(policy_action: str, model_context: str) -> str:
        """Tiny deterministic assistant stub used by the smoke path."""
        if not model_context:
            return "No prior frame context is available."
        if policy_action == "ignore_screen_instruction":
            return "I noticed something about hidden fields in the previous frame."
        return f"Guarded action={policy_action}; context={model_context}"
