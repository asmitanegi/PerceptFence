"""Deterministic held-out adversarial case generator.

Given a seed, produce a census of EvasionCase objects by applying self-authored,
literature-informed evasion-family templates (taxonomy.py) to synthetic payloads in
benign carriers. The generator does not import the redactor or inspect its output at
runtime, but generator, oracle, and defence were developed in the same project; this
is a deterministic synthetic stress test, not independent red teaming. See PROTOCOL.md.
"""

from __future__ import annotations

import random

from taxonomy import (
    BENIGN_CARRIERS,
    BENIGN_TOKENS,
    EvasionCase,
    FAMILY_COVERAGE,
    PAYLOAD_CLASSES,
    SINGLE_OPERATORS,
    _apply_zero_width,
    _apply_confusable,
)

# Which payload classes each family is exercised against.
FAMILY_PAYLOADS: dict[str, tuple[str, ...]] = {
    "unicode_confusable": ("credential", "email"),
    "zero_width": ("credential", "ssn", "card", "email"),
    "digit_split": ("ssn", "card"),
    "fullwidth_compat": ("credential", "ssn", "card", "email"),
    "base64": ("credential", "ssn", "card", "email"),
    "hex": ("credential", "ssn", "card"),
    "rot13": ("credential", "email"),
    "leetspeak": ("credential",),
    "bidi_override": ("credential", "email"),
    "instruction_paraphrase": ("injection",),
    "chained": ("credential", "ssn", "card"),
}

INTENSITIES = (1, 2, 3, 4)


def _canonical_secret(payload_class: str, raw: str) -> str:
    """The ground-truth secret string whose recoverability the oracle checks.

    For keyword=value credentials and instructions we use the whole payload; for
    digit PII we use the digit string (the sensitive part).
    """
    if payload_class in ("ssn", "card"):
        return "".join(c for c in raw if c.isdigit())
    if payload_class == "credential":
        return raw.split("=", 1)[-1].split(" ", 1)[-1]
    return raw


def _embed(carrier_idx: int, transformed: str, rng: random.Random) -> tuple[str, tuple[str, ...]]:
    carrier = BENIGN_CARRIERS[carrier_idx % len(BENIGN_CARRIERS)].format(n=rng.randint(10, 99))
    benign = tuple(t for t in BENIGN_TOKENS if t in carrier)
    rendered = f"{carrier}\n{transformed}"
    return rendered, benign


def generate(seed: int) -> list[EvasionCase]:
    rng = random.Random(seed)
    cases: list[EvasionCase] = []
    carrier_idx = 0

    for family, payload_classes in FAMILY_PAYLOADS.items():
        coverage = FAMILY_COVERAGE[family]
        for pclass in payload_classes:
            for raw in PAYLOAD_CLASSES[pclass]:
                secret = _canonical_secret(pclass, raw)
                for intensity in INTENSITIES:
                    if family == "chained":
                        # compose two operators: confusable/zero-width then base64-free
                        # split, so it lands partly in and partly out of coverage.
                        step1 = _apply_confusable(raw, rng, density=0.4)
                        transformed = _apply_zero_width(step1, rng, count=intensity)
                    else:
                        op = SINGLE_OPERATORS[family]
                        transformed = op(raw, rng, intensity)
                    rendered, benign = _embed(carrier_idx, transformed, rng)
                    carrier_idx += 1
                    cases.append(
                        EvasionCase(
                            family=family,
                            coverage=coverage,
                            payload_class=pclass,
                            raw_payload=secret,
                            transformed=transformed,
                            rendered=rendered,
                            benign_tokens=benign,
                            intensity=intensity,
                        )
                    )
    return cases


def generate_benign(seed: int, n: int = 40) -> list[EvasionCase]:
    """Benign controls for the separate sentinel-token removal proxy."""
    rng = random.Random(seed + 10_000)
    cases: list[EvasionCase] = []
    for i in range(n):
        carrier = BENIGN_CARRIERS[i % len(BENIGN_CARRIERS)].format(n=rng.randint(10, 99))
        benign = tuple(t for t in BENIGN_TOKENS if t in carrier)
        cases.append(
            EvasionCase(
                family="benign_control",
                coverage="n/a",
                payload_class="none",
                raw_payload="",
                transformed="",
                rendered=carrier,
                benign_tokens=benign,
                intensity=0,
            )
        )
    return cases


if __name__ == "__main__":
    c = generate(0)
    print(f"seed 0: {len(c)} payload-bearing cases across {len(FAMILY_PAYLOADS)} families")
    from collections import Counter
    for fam, k in sorted(Counter(x.family for x in c).items()):
        print(f"  {fam:24} {k:3d}  ({FAMILY_COVERAGE[fam]})")
    print(f"benign controls: {len(generate_benign(0))}")
