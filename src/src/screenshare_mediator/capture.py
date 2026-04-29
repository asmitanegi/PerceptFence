"""Synthetic screen/speech capture adapter.

This adapter intentionally reads only fixture dictionaries. It is the seam where
real capture code would plug in after the filing gate; the pre-filing prototype
keeps live screen, microphone, and network access out of scope.
"""

from __future__ import annotations

from typing import Any

from .models import CapturedSession


class SyntheticCaptureAdapter:
    """Normalize one synthetic fixture into a captured session."""

    def capture(self, fixture: dict[str, Any]) -> CapturedSession:
        payload = fixture["input"]
        return CapturedSession(
            fixture_id=fixture["id"],
            scenario_class=fixture["scenario_class"],
            modalities=tuple(fixture["modality"]),
            window_title=payload.get("window_title"),
            screen_text=payload.get("visible_text", ""),
            speech_transcript=payload.get("transcript", ""),
            notification_text=payload.get("notification_text", ""),
            events=tuple(payload.get("events", ())),
            layout=dict(payload.get("layout", {})),
        )
