"""Tests for the held-out adversarial evaluation harness.

Covers the anti-circularity controls required by eval/heldout/PROTOCOL.md:
  - oracle positive control: a payload the redactor is known to MISS must be flagged
    exposed (checks a separately implemented oracle path; it does not establish
    statistical independence or a semantic-superset relationship);
  - oracle negative control: benign text yields no exposure;
  - generator determinism and family coverage;
  - in-coverage sanity: PerceptFence beats the no-normalization naive baseline on a
    normalization family.
"""

from __future__ import annotations

import base64
import pathlib
import sys

_HELDOUT = pathlib.Path(__file__).resolve().parents[1] / "eval" / "heldout"
sys.path.insert(0, str(_HELDOUT))

import oracle  # noqa: E402
import generator  # noqa: E402
import taxonomy  # noqa: E402
from baselines import naive_redact, perceptfence_redact  # noqa: E402


def test_oracle_is_independent_of_redactor_source():
    # The oracle must not IMPORT the redactor (no shared-normalization circularity).
    # We inspect actual import statements via AST, not prose mentions in the docstring.
    import ast
    tree = ast.parse((_HELDOUT / "oracle.py").read_text())
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert not any("redaction" in m or "screenshare_mediator" in m for m in imported), imported


def test_oracle_positive_control_catches_known_miss():
    # PerceptFence has no base64 decoder -> it leaves the payload intact -> the oracle,
    # on this separately implemented path, must recover it and report exposed. This
    # positive control does not prove statistical independence or general superiority.
    secret = "SKDEMO1234ABCDxyz7890"  # synthetic demo fixture, not a real credential (smoke: allow)
    b64 = base64.b64encode(("api_key=" + secret).encode()).decode()
    pf_out = perceptfence_redact("value: " + b64)
    assert secret in pf_out or b64 in pf_out  # redactor genuinely did not remove it
    assert oracle.is_exposed(pf_out, secret) is True


def test_oracle_negative_control_clean_text():
    assert oracle.is_exposed("deploy build 42 to the sandbox environment", "") is False
    # a benign carrier with no injected payload exposes nothing
    benign = generator.generate_benign(0)[0]
    assert oracle.is_exposed(perceptfence_redact(benign.rendered), benign.raw_payload) is False


def test_oracle_detects_leet_encoded_secret():
    secret = "SKDEMO1234ABCDxyz7890"  # synthetic demo fixture, not a real credential (smoke: allow)
    leet = "".join({"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7", "l": "1"}
                    .get(c.lower(), c) for c in secret)
    assert oracle.is_exposed("token: " + leet, secret) is True


def test_generator_deterministic():
    a = generator.generate(3)
    b = generator.generate(3)
    assert [c.rendered for c in a] == [c.rendered for c in b]
    c = generator.generate(4)
    assert [x.rendered for x in a] != [x.rendered for x in c]


def test_generator_covers_all_families():
    fams = {c.family for c in generator.generate(0)}
    assert fams == set(taxonomy.FAMILY_COVERAGE)
    # coverage labels are well-formed
    assert set(taxonomy.FAMILY_COVERAGE.values()) <= {"in", "partial", "out"}


def test_perceptfence_beats_naive_on_confusable_family():
    cases = [c for c in generator.generate(0) if c.family == "unicode_confusable"]
    assert cases
    pf = sum(0 if oracle.is_exposed(perceptfence_redact(c.rendered), c.raw_payload) else 1
             for c in cases)
    nv = sum(0 if oracle.is_exposed(naive_redact(c.rendered), c.raw_payload) else 1
             for c in cases)
    assert pf > nv  # normalization-first redaction wins where it has coverage


def test_perceptfence_honestly_misses_base64_family():
    # Out-of-coverage family: recall should be low (honest miss), not perfect.
    cases = [c for c in generator.generate(0) if c.family == "base64"]
    neutralized = sum(0 if oracle.is_exposed(perceptfence_redact(c.rendered), c.raw_payload)
                      else 1 for c in cases)
    assert neutralized / len(cases) < 0.2
