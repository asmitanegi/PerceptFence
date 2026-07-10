"""Defenses compared on the held-out census. Uniform interface: redact(text) -> text.

- naive       : basic regex DLP, NO normalization (no NFKC/confusable/zero-width/decode).
- perceptfence: the repository RedactionEngine under the `redact_before_model` action
                (exercises all six transform families). The system under test.
- presidio    : REAL Microsoft Presidio (presidio-analyzer + spaCy en_core_web_sm NER +
                predefined pattern recognizers), run offline. Detected spans -> placeholder.
                Imported lazily so the std-lib defenses run without Presidio installed.

The same separately implemented oracle (oracle.py) is applied to every defense's
output. Equal scoring code improves comparability but does not make the oracle
methodologically independent of this self-authored study.
"""

from __future__ import annotations

import re

# --- naive baseline (no normalization) --------------------------------------------------
_NAIVE_PATTERNS = [
    re.compile(r"(?i)\b(api[_\s-]?key|secret|password|pwd|access[_\s-]?token|bearer)\b[\s=:]*\S+"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b\d{13,16}\b"),
    re.compile(r"\b[\w.%+-]+@[\w.-]+\.\w+\b"),
]


def naive_redact(text: str) -> str:
    for pat in _NAIVE_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


# --- perceptfence (system under test) ---------------------------------------------------
_pf_adapter = None
_pf_engine = None


def perceptfence_redact(text: str) -> str:
    global _pf_adapter, _pf_engine
    if _pf_engine is None:
        from screenshare_mediator.capture import SyntheticCaptureAdapter
        from screenshare_mediator.redaction import RedactionEngine
        _pf_adapter = SyntheticCaptureAdapter()
        _pf_engine = RedactionEngine()
    from screenshare_mediator.models import PolicyDecision
    fixture = {
        "id": "heldout",
        "scenario_class": "terminal_secret",
        "modality": ["screen_text"],
        "input": {"window_title": "", "visible_text": text},
    }
    cap = _pf_adapter.capture(fixture)
    dec = PolicyDecision("heldout", "terminal_secret", "redact_before_model", "held-out eval")
    return _pf_engine.mediate(cap, dec).model_context


# --- real Presidio baseline (lazy) ------------------------------------------------------
_presidio_analyzer = None


def presidio_available() -> bool:
    try:
        import presidio_analyzer  # noqa: F401
        return True
    except Exception:
        return False


def _get_presidio():
    global _presidio_analyzer
    if _presidio_analyzer is None:
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        cfg = {"nlp_engine_name": "spacy",
               "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]}
        nlp = NlpEngineProvider(nlp_configuration=cfg).create_engine()
        _presidio_analyzer = AnalyzerEngine(nlp_engine=nlp)
    return _presidio_analyzer


def presidio_redact(text: str) -> str:
    analyzer = _get_presidio()
    results = analyzer.analyze(text=text, language="en")
    # Replace detected spans right-to-left to keep offsets valid.
    spans = sorted(results, key=lambda r: r.start, reverse=True)
    chars = list(text)
    for r in spans:
        chars[r.start:r.end] = list("[REDACTED]")
    return "".join(chars)


DEFENSES = {
    "naive": naive_redact,
    "perceptfence": perceptfence_redact,
    "presidio": presidio_redact,  # gated at runtime by presidio_available()
}
