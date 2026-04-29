"""Load and validate synthetic screen-share assistant fixtures.

The module intentionally uses only the Python standard library so the smoke test
can run in an offline fresh checkout.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EXPECTED_SCENARIO_CLASSES = (
    "terminal_secret",
    "chat_notification",
    "browser_pii",
    "spoken_sensitive_fragment",
    "prompt_injection_on_screen",
    "fast_window_switching",
    "small_font_zoomed_ui",
    "homoglyph_credential",
    "split_pii",
    "mixed_sensitivity",
)

REQUIRED_FIXTURE_FIELDS = {
    "id",
    "scenario_class",
    "modality",
    "synthetic",
    "risk_label",
    "input",
    "expected_policy_action",
}


def load_fixture_index(repo_root: Path | None = None) -> list[dict[str, Any]]:
    """Return all synthetic fixtures listed in data/synthetic/index.json."""
    root = repo_root or Path(__file__).resolve().parents[2]
    index_path = root / "data" / "synthetic" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    fixtures = []
    for entry in index["fixtures"]:
        fixture_path = index_path.parent / entry["file"]
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["_file"] = entry["file"]
        fixtures.append(fixture)
    return fixtures


def validate_fixture_set(fixtures: list[dict[str, Any]]) -> None:
    """Raise ValueError if fixture coverage or schema is incomplete."""
    seen = set()
    for fixture in fixtures:
        missing = REQUIRED_FIXTURE_FIELDS - set(fixture)
        if missing:
            raise ValueError(f"{fixture.get('id', '<unknown>')} missing fields: {sorted(missing)}")
        if fixture["synthetic"] is not True:
            raise ValueError(f"{fixture['id']} must be marked synthetic=true")
        scenario_class = fixture["scenario_class"]
        if scenario_class not in EXPECTED_SCENARIO_CLASSES:
            raise ValueError(f"{fixture['id']} has unknown scenario_class {scenario_class!r}")
        seen.add(scenario_class)

    expected = set(EXPECTED_SCENARIO_CLASSES)
    if seen != expected:
        raise ValueError(f"scenario coverage mismatch: missing={sorted(expected-seen)} extra={sorted(seen-expected)}")
