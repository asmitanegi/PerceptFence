"""Output guard for deterministic smoke-path assistant responses.

The guard is deliberately rule-based for the anonymous scaffold. Its decision
context is separate from the assistant model context: callers pass only the
assistant candidate output plus policy metadata, never the raw/mediated screen
context that may contain prompt-injection text.
"""

from __future__ import annotations

import re

from .models import OutputGuardContext, OutputGuardDecision, PolicyDecision


class OutputGuard:
    """Filter assistant output without sharing assistant model context."""

    _ACTION_CATEGORIES = {
        "redact_before_model": ("credential", "token"),
        "suppress_notification": ("notification", "private message"),
        "summarize_without_identifier": ("identifier", "email", "record"),
        "ignore_screen_instruction": ("screen instruction", "hidden field"),
        "require_stable_window": ("unstable window",),
        "increase_ocr_sensitivity": ("low-visibility content",),
        "selective_redact": ("non-consented region", "credential", "ssh command"),
        "block_memory_write": ("spoken secret", "recovery phrase"),
    }

    _BLOCKED_FRAGMENTS = (
        "DEMO_SECRET_TOKEN_12345",
        "alex.example.invalid",
        "SYN-000-42",
        "blue comet seven",
        "hide the draft budget line",
        "SYSTEM OVERRIDE",
        "АKIА1234EXАMPLE5678",
        "wJаlrXUtnFEMI/K7MDENG/bPxRfiCYEXАMPLEKEY",
        "1 2 3 - 4 5 - 6 7 8 9",
        "DEMO_sk_live_12345abcXYZ",
        "ssh deploy@staging.example.invalid",
    )

    _INDIRECT_DISCLOSURE_RE = re.compile(
        r"(?ix)"
        r"\b("
        r"noticed|saw|observed|found|detected|remember|recall|can't\s+show|cannot\s+show|won't\s+show"
        r")\b"
        r".{0,80}"
        r"\b("
        r"credential|credentials|api\s*key|secret|token|hidden\s+fields?|recovery\s+phrase|"
        r"ssn|social\s+security|email|record|identifier|private\s+message"
        r")\b"
    )

    @classmethod
    def context_from_policy(cls, decision: PolicyDecision) -> OutputGuardContext:
        """Build the guard's isolated policy-only context."""
        return OutputGuardContext(
            fixture_id=decision.fixture_id,
            scenario_class=decision.scenario_class,
            policy_action=decision.action,
            policy_reason=decision.reason,
            blocked_categories=cls._ACTION_CATEGORIES.get(decision.action, ()),
        )

    def guard(self, output: str, context: OutputGuardContext) -> OutputGuardDecision:
        """Return an output verdict using only candidate output + guard context."""
        if any(fragment in output for fragment in self._BLOCKED_FRAGMENTS):
            return OutputGuardDecision(
                fixture_id=context.fixture_id,
                scenario_class=context.scenario_class,
                action="block_output",
                reason=f"literal sensitive fragment blocked for {context.policy_action}",
                allowed=False,
                replacement=f"[OUTPUT BLOCKED: {context.policy_action}]",
            )

        indirect_match = self._INDIRECT_DISCLOSURE_RE.search(output)
        if indirect_match:
            return OutputGuardDecision(
                fixture_id=context.fixture_id,
                scenario_class=context.scenario_class,
                action="block_output",
                reason=f"indirect disclosure blocked for {context.policy_action}",
                allowed=False,
                replacement=f"[OUTPUT BLOCKED: {context.policy_action}]",
            )

        if context.policy_action == "require_stable_window":
            return OutputGuardDecision(
                fixture_id=context.fixture_id,
                scenario_class=context.scenario_class,
                action="hold_output",
                reason="unstable window context held",
                allowed=False,
                replacement="[OUTPUT HELD: unstable window context]",
            )

        return OutputGuardDecision(
            fixture_id=context.fixture_id,
            scenario_class=context.scenario_class,
            action="allow_output",
            reason=f"no output-guard rule matched for {context.policy_action}",
            allowed=True,
        )

    @staticmethod
    def apply(output: str, decision: OutputGuardDecision) -> str:
        """Return the candidate output or the guard replacement text."""
        return output if decision.allowed else decision.replacement or "[OUTPUT BLOCKED]"
