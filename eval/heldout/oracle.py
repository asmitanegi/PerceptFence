"""Separately implemented exposure oracle with different normalization semantics.

This module shares no imports with ``screenshare_mediator.redaction`` and adds
base64, hex, and ROT13 decoding paths. It was nevertheless designed by the same
authors and is neither methodologically independent nor a semantic superset of the
redactor. In particular, their confusable tables differ, and the Greek-alpha witness
documented in ``PROTOCOL.md`` is detected by the redactor but missed here.

A payload is EXPOSED if, after maximal normalization of a defense's output, either the
full canonical secret survives, or a contiguous canonical substring of length
>= ceil(0.7 * |secret|) survives (partial-mask recoverability). Otherwise NEUTRALIZED.
"""

from __future__ import annotations

import base64
import binascii
import codecs
import math
import re
import unicodedata

# Confusable fold used by this oracle; intentionally not claimed as a superset.
_CONFUSABLE_BACK = {
    "а": "a", "с": "c", "е": "e", "і": "i", "ј": "j", "о": "o", "р": "p", "ѕ": "s",
    "х": "x", "у": "y", "А": "a", "В": "b", "С": "c", "Е": "e", "Н": "h", "К": "k",
    "М": "m", "О": "o", "Р": "p", "Т": "t", "Х": "x", "Ү": "y", "η": "n", "ν": "v",
    "κ": "k", "Α": "a", "Β": "b", "Ε": "e", "Ι": "i", "Κ": "k", "Μ": "m", "Ν": "n",
    "Ο": "o", "Ρ": "p", "Τ": "t", "Υ": "y", "Χ": "x", "Ζ": "z",
}
_FORMAT_BIDI = "".join((
    "​", "‌", "‍", "﻿", "⁠",       # zero-width / format
    "‪", "‫", "‬", "‭", "‮",       # bidi embeddings/overrides
    "⁦", "⁧", "⁨", "⁩",                 # isolates
))
_FORMAT_RE = re.compile("[" + re.escape(_FORMAT_BIDI) + "]")
_B64_RE = re.compile(r"[A-Za-z0-9+/]{12,}={0,2}")
_HEX_RE = re.compile(r"(?:[0-9a-fA-F]{2}){8,}")


def _strip_accents(s: str) -> str:
    # NFKD then drop combining marks; folds full-width and many compatibility forms.
    decomposed = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _confusable_fold(s: str) -> str:
    return "".join(_CONFUSABLE_BACK.get(ch, ch) for ch in s)


def _decode_layers(s: str) -> list[str]:
    """Return candidate decodings (base64/hex/rot13) found anywhere in s, plus s itself."""
    out = [s]
    out.append(codecs.decode(s, "rot_13"))
    for m in _B64_RE.findall(s):
        try:
            dec = base64.b64decode(m + "=" * (-len(m) % 4), validate=False)
            out.append(dec.decode("utf-8", "ignore"))
        except (binascii.Error, ValueError):
            pass
    for m in _HEX_RE.findall(s):
        try:
            out.append(bytes.fromhex(m).decode("utf-8", "ignore"))
        except ValueError:
            pass
    return out


def _canon(s: str) -> str:
    s = _FORMAT_RE.sub("", s)
    s = _strip_accents(s)
    s = _confusable_fold(s)
    s = re.sub(r"[\s\-_]", "", s)
    return s.lower()


def maximal_forms(s: str) -> list[str]:
    """All canonical forms of s, including post-decode canonicalizations."""
    forms = set()
    for layer in _decode_layers(s):
        forms.add(_canon(layer))
        # also canon-then-decode for confusable-wrapped encodings
    forms.add(_canon(s))
    return [f for f in forms if f]


# Leetspeak fold: letter -> common substitution. Applied to the SECRET to build an attack
# variant (not to the whole text — folding digits would corrupt digit-PII secrets).
_LEET_ENCODE = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7", "l": "1"}


def _leet_variant(target: str) -> str:
    return "".join(_LEET_ENCODE.get(ch, ch) for ch in target)


def is_exposed(defense_output: str, canonical_secret: str) -> bool:
    """True if the secret is recoverable from the defense output (a MISS by the defense)."""
    if not canonical_secret:
        return False
    base = _canon(canonical_secret)
    if not base:
        return False
    # The maximal adversary also recognizes a leet-encoded rendering of the secret.
    targets = {base, _leet_variant(base)}
    forms = maximal_forms(defense_output)
    for target in targets:
        thresh = math.ceil(0.7 * len(target))
        for form in forms:
            if target in form:
                return True
            # partial-mask recoverability: contiguous run of target present
            for start in range(0, len(target) - thresh + 1):
                if target[start:start + thresh] in form:
                    return True
    return False


def benign_blocked(defense_output: str, benign_tokens: tuple[str, ...]) -> int:
    """Count benign task-critical tokens that did NOT survive (false blocks)."""
    canon_out = _canon(defense_output)
    return sum(1 for t in benign_tokens if _canon(t) not in canon_out)
