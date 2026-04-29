"""Consent/policy engine for the synthetic runtime smoke path."""

from __future__ import annotations

import json
from pathlib import Path

from .models import CapturedSession, PolicyDecision


ACTION_BY_SCENARIO_CLASS = {
    "terminal_secret": "redact_before_model",
    "chat_notification": "suppress_notification",
    "browser_pii": "summarize_without_identifier",
    "spoken_sensitive_fragment": "block_memory_write",
    "prompt_injection_on_screen": "ignore_screen_instruction",
    "fast_window_switching": "require_stable_window",
    "small_font_zoomed_ui": "increase_ocr_sensitivity",
    "homoglyph_credential": "redact_before_model",
    "split_pii": "redact_before_model",
    "mixed_sensitivity": "selective_redact",
}


class ConsentPolicyEngine:
    """Choose one policy action for a captured synthetic session."""

    def __init__(self, allowed_actions: set[str]) -> None:
        self.allowed_actions = allowed_actions

    @classmethod
    def from_policy_file(cls, path: Path) -> "ConsentPolicyEngine":
        policy = json.loads(path.read_text(encoding="utf-8"))
        return cls(set(policy["allowed_actions"]))

    def decide(self, session: CapturedSession) -> PolicyDecision:
        action = ACTION_BY_SCENARIO_CLASS[session.scenario_class]
        if action not in self.allowed_actions:
            raise ValueError(f"policy action {action!r} is not allowed")
        return PolicyDecision(
            fixture_id=session.fixture_id,
            scenario_class=session.scenario_class,
            action=action,
            reason=f"synthetic {session.scenario_class} fixture maps to {action}",
        )
