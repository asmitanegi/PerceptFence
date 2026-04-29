"""Offline smoke test for the anonymous synthetic runtime scaffold."""

from __future__ import annotations

from pathlib import Path
import json

from screenshare_mediator import EXPECTED_SCENARIO_CLASSES, RuntimeMediator, load_fixture_index, validate_fixture_set


SENSITIVE_SENTINEL = "DEMO_SECRET_TOKEN_12345"
SSN_SENTINEL = "123-45-6789"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    fixtures = load_fixture_index(repo_root)
    validate_fixture_set(fixtures)

    policy_path = repo_root / "policies" / "consent_redaction_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    required_actions = {fixture["expected_policy_action"] for fixture in fixtures}
    allowed_actions = set(policy["allowed_actions"])
    unknown_actions = required_actions - allowed_actions
    if unknown_actions:
        raise SystemExit(f"Unknown policy actions: {sorted(unknown_actions)}")

    runtime = RuntimeMediator(policy_path)
    terminal_secret = next(fixture for fixture in fixtures if fixture["scenario_class"] == "terminal_secret")
    baseline = runtime.run_baseline(terminal_secret)
    guarded = runtime.run_guarded(terminal_secret)

    baseline_exposed = SENSITIVE_SENTINEL in baseline.model_context
    guarded_exposed = SENSITIVE_SENTINEL in guarded.model_context
    if not baseline_exposed:
        raise SystemExit("Baseline smoke path did not expose the synthetic sentinel as expected")
    if guarded_exposed:
        raise SystemExit("Guarded smoke path failed to mediate the synthetic sentinel")
    if len(guarded.audit_events) != 2:
        raise SystemExit("Guarded smoke path did not record policy + output-guard audit events")

    prompt_injection = next(fixture for fixture in fixtures if fixture["scenario_class"] == "prompt_injection_on_screen")
    injection_baseline = runtime.run_baseline(prompt_injection)
    injection_guarded = runtime.run_guarded(prompt_injection)
    baseline_leaked_instruction = "system override" in injection_baseline.assistant_output.lower()
    separate_guard_blocked = injection_guarded.assistant_output == "[OUTPUT BLOCKED: ignore_screen_instruction]"
    guard_logged = any(
        event.get("event_type") == "output_guard_decision" and event.get("allowed") == "false"
        for event in injection_guarded.audit_events
    )
    if not baseline_leaked_instruction:
        raise SystemExit("Prompt-injection baseline did not expose the synthetic injection as expected")
    if not separate_guard_blocked or not guard_logged:
        raise SystemExit("Separate-context output guard did not block/log prompt-injection leakage")

    spoken_sensitive = next(fixture for fixture in fixtures if fixture["scenario_class"] == "spoken_sensitive_fragment")
    memory_baseline = runtime.run_baseline(spoken_sensitive)
    memory_guarded = runtime.run_guarded(spoken_sensitive)
    baseline_reproduced_ssn = SSN_SENTINEL in memory_baseline.assistant_output
    context_excluded_ssn = SSN_SENTINEL not in memory_guarded.model_context
    context_excluded_phrase = "blue comet seven" not in memory_guarded.assistant_output
    exclusion_logged = any(event.get("event_type") == "context_exclusion" for event in memory_guarded.audit_events)
    if not baseline_reproduced_ssn:
        raise SystemExit("Memory-gate baseline did not reproduce the excluded SSN as expected")
    if not context_excluded_ssn or not context_excluded_phrase or not exclusion_logged:
        raise SystemExit("Context-exclusion memory gate failed to exclude/log the revoked-consent content")

    classes = ", ".join(EXPECTED_SCENARIO_CLASSES)
    print(f"Validated scenario classes: {classes}")
    print(
        "Baseline path: "
        f"fixture={baseline.fixture_id} model_context_contains_sentinel={baseline_exposed}"
    )
    print(
        "Guarded path: "
        f"fixture={guarded.fixture_id} action={guarded.audit_events[0]['action']} "
        f"model_context_contains_sentinel={guarded_exposed} audit_events={len(guarded.audit_events)}"
    )
    print(
        "Prompt-injection path: "
        f"baseline_leaked_instruction={baseline_leaked_instruction} "
        f"separate_context_guard_blocked={separate_guard_blocked} "
        f"output_guard_logged={guard_logged}"
    )
    print(
        "Context-exclusion path: "
        f"baseline_reproduced_ssn={baseline_reproduced_ssn} "
        f"guarded_context_contains_ssn={not context_excluded_ssn} "
        f"guarded_output_mentions_phrase={not context_excluded_phrase} "
        f"context_exclusion_logged={exclusion_logged}"
    )
    print(f"SMOKE PASS: {len(fixtures)} synthetic scenarios validated; 3 runtime mediation paths exercised")


if __name__ == "__main__":
    main()
