"""Redaction engine for model context construction."""

from __future__ import annotations

import re
import unicodedata

from .models import CapturedSession, MediatedSession, PolicyDecision


class RedactionEngine:
    """Apply the selected policy action before content reaches model context.

    Screen text is treated as untrusted input. Policy actions may suppress or
    summarize differently, but every path runs deterministic sanitizers before
    text is returned as model context.
    """

    _ZERO_WIDTH_CHARS = "\u200b\u200c\u200d\ufeff"
    _SEP_CHARS = rf"[ \t\-{_ZERO_WIDTH_CHARS}]*"
    _DIGIT_WITH_GAP = rf"\d[ \t{_ZERO_WIDTH_CHARS}]*"

    _CONFUSABLES = str.maketrans(
        {
            # Cyrillic lookalikes commonly used in credential/PII evasion.
            "А": "A",
            "В": "B",
            "Е": "E",
            "К": "K",
            "М": "M",
            "Н": "H",
            "О": "O",
            "Р": "P",
            "С": "C",
            "Т": "T",
            "У": "Y",
            "Х": "X",
            "а": "a",
            "е": "e",
            "о": "o",
            "р": "p",
            "с": "c",
            "у": "y",
            "х": "x",
            "і": "i",
            "ј": "j",
            # Greek lookalikes seen in pasted screen text.
            "Α": "A",
            "Β": "B",
            "Ε": "E",
            "Η": "H",
            "Ι": "I",
            "Κ": "K",
            "Μ": "M",
            "Ν": "N",
            "Ο": "O",
            "Ρ": "P",
            "Τ": "T",
            "Χ": "X",
            "Υ": "Y",
            "Ζ": "Z",
            "α": "a",
            "β": "b",
            "ε": "e",
            "η": "h",
            "ι": "i",
            "κ": "k",
            "ν": "v",
            "ο": "o",
            "ρ": "p",
            "τ": "t",
            "χ": "x",
            "υ": "y",
            "ζ": "z",
        }
    )
    _CONFUSABLE_CHAR_RE = re.compile("[" + re.escape("".join(chr(c) for c in _CONFUSABLES)) + "]")

    _CREDENTIAL_RE = re.compile(
        r"(?i)(?<!\w)((?:--?)?(?:api[-_\s]?key|access[-_\s]?token|auth[-_\s]?token|"
        r"bearer[-_\s]?token|aws[-_\s]?access[-_\s]?key[-_\s]?id|aws[-_\s]?secret[-_\s]?access[-_\s]?key|access[-_\s]?key|token|secret|password|pwd)\b\s*(?:=|:)?\s*)"
        r"[A-Za-z0-9._~+/=-]{6,}"
    )
    _BEARER_RE = re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]{8,}")
    _ORPHAN_CREDENTIAL_VALUE_RE = re.compile(r"\b[A-Z0-9_-]*(?:SECRET|TOKEN|API[_-]?KEY)[A-Z0-9_-]*\b")
    _CREDENTIAL_SIGNAL_RE = re.compile(
        r"(?i)\b(api[-_\s]?key|access[-_\s]?token|auth[-_\s]?token|bearer|aws[-_\s]?access[-_\s]?key[-_\s]?id|aws[-_\s]?secret[-_\s]?access[-_\s]?key|access[-_\s]?key|token|secret|password|pwd)\b"
    )
    _CREDENTIAL_VALUE_RE = re.compile(
        r"(?i)\b(?:sk|pk|ghp|demo|synthetic)?[-_A-Z0-9]{8,}\b|"
        r"\b[A-Z0-9_-]*(?:SECRET|TOKEN|KEY)[A-Z0-9_-]*\b"
    )
    _PROMPT_INJECTION_RE = re.compile(
        r"(?is)\b(ignore|bypass|disable|override)\b.{0,100}\b(redaction|policy|policies|guard|system|instruction)\b|"
        r"\b(repeat|reveal|print|show)\b.{0,100}\b(api[-_\s]?key|secret|token|hidden field|verbatim)\b"
    )
    _EMAIL_RE = re.compile(r"\b[\w.%-]+@?[\w.-]+\.invalid\b|\b[\w.%-]+@[\w.-]+\b")
    _RECORD_RE = re.compile(r"\bSYN-\d{3}-\d{2}\b")
    _NAME_RE = re.compile(r"(?im)^Name:\s*[^\n]+")
    _SSN_RE = re.compile(
        rf"(?<!\d)(?:{_DIGIT_WITH_GAP}){{3}}{_SEP_CHARS}"
        rf"(?:{_DIGIT_WITH_GAP}){{2}}{_SEP_CHARS}"
        rf"(?:{_DIGIT_WITH_GAP}){{4}}(?![ \t{_ZERO_WIDTH_CHARS}]*\d)"
    )
    _CARD_CANDIDATE_RE = re.compile(rf"(?<!\d)(?:\d[ \t\-{_ZERO_WIDTH_CHARS}]*){{13,19}}(?!\d)")

    def mediate(self, session: CapturedSession, decision: PolicyDecision) -> MediatedSession:
        action = decision.action
        context = self._sanitize_untrusted_text(session.raw_context)

        if action in {"redact_before_model", "selective_redact"}:
            pass
        elif action == "suppress_notification":
            context = self._sanitize_untrusted_text(
                "\n".join(chunk for chunk in [session.window_title or "", session.screen_text] if chunk)
            )
        elif action == "summarize_without_identifier":
            context = self._summarize_identifiers(context)
        elif action == "ignore_screen_instruction":
            context = self._redact_prompt_injections(context)
        elif action == "require_stable_window":
            context = "[HELD UNTIL WINDOW STABLE]"
        elif action == "increase_ocr_sensitivity":
            context = f"[OCR sensitivity increased]\n{context}"
        elif action == "selective_redact":
            context = self._redact_nonconsented_region(context)
        elif action == "block_memory_write":
            pass
        else:
            raise ValueError(f"unsupported policy action {action!r}")

        return MediatedSession(
            fixture_id=session.fixture_id,
            scenario_class=session.scenario_class,
            model_context=context,
            decision=decision,
            memory_allowed=action != "block_memory_write",
        )

    def detection_categories(self, text: str) -> tuple[str, ...]:
        """Return deterministic evasion categories observed in text.

        This is intentionally small and fixture-oriented so eval reports can
        break detection down by technique without pretending to cover unknown
        credential formats.
        """
        normalized = self._normalize_for_detection(text)
        categories: set[str] = set()
        if self._PROMPT_INJECTION_RE.search(normalized):
            categories.add("prompt_injection")
        if self._CONFUSABLE_CHAR_RE.search(text) and self._line_has_credential_signal(normalized):
            categories.add("homoglyph_credential")
        if self._SSN_RE.search(text) or self._has_luhn_card(text):
            categories.add("split_digit_pii")
        if self._CREDENTIAL_RE.search(normalized) or self._BEARER_RE.search(normalized):
            categories.add("credential")
        return tuple(sorted(categories))

    def _sanitize_untrusted_text(self, text: str) -> str:
        # Homoglyph credentials are line-redacted before ASCII regexes can
        # partially mask only the prefix and leave the confusable suffix behind.
        text = self._redact_homoglyph_credentials(text)
        text = self._redact_split_digit_pii(text)
        text = self._redact_credentials(text)
        text = self._summarize_identifiers(text)
        return self._redact_prompt_injections(text)

    def _redact_credentials(self, text: str) -> str:
        text = self._CREDENTIAL_RE.sub(r"\1[REDACTED]", text)
        text = self._BEARER_RE.sub(r"\1[REDACTED]", text)
        return self._ORPHAN_CREDENTIAL_VALUE_RE.sub("[REDACTED CREDENTIAL]", text)

    def _summarize_identifiers(self, text: str) -> str:
        text = self._EMAIL_RE.sub("[EMAIL]", text)
        text = self._RECORD_RE.sub("[RECORD]", text)
        return self._NAME_RE.sub("Name: [PERSON]", text)

    def _redact_split_digit_pii(self, text: str) -> str:
        text = self._CARD_CANDIDATE_RE.sub(self._redact_card_if_valid, text)
        return self._SSN_RE.sub("[SSN]", text)

    def _redact_card_if_valid(self, match: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        if 13 <= len(digits) <= 19 and self._luhn_valid(digits):
            return "[CARD]"
        return match.group(0)

    def _has_luhn_card(self, text: str) -> bool:
        return any(self._redact_card_if_valid(match) == "[CARD]" for match in self._CARD_CANDIDATE_RE.finditer(text))

    @staticmethod
    def _luhn_valid(digits: str) -> bool:
        total = 0
        parity = len(digits) % 2
        for index, char in enumerate(digits):
            value = int(char)
            if index % 2 == parity:
                value *= 2
                if value > 9:
                    value -= 9
            total += value
        return total % 10 == 0

    def _redact_prompt_injections(self, text: str) -> str:
        return "\n".join(
            "[SCREEN INSTRUCTION IGNORED]"
            if self._PROMPT_INJECTION_RE.search(self._normalize_for_detection(line))
            else line
            for line in text.splitlines()
        )

    def _redact_homoglyph_credentials(self, text: str) -> str:
        lines = []
        for line in text.splitlines():
            normalized = self._normalize_for_detection(line)
            if normalized != line and self._line_has_credential_signal(normalized):
                lines.append("[REDACTED CREDENTIAL]")
            else:
                lines.append(line)
        return "\n".join(lines)

    def _redact_nonconsented_region(self, text: str) -> str:
        """Drop the explicitly non-consented pane while preserving consented content."""
        lines = []
        in_nonconsented_region = False
        redaction_inserted = False
        for line in text.splitlines():
            if "RIGHT PANE" in line and "non-consented" in line.lower():
                in_nonconsented_region = True
                if not redaction_inserted:
                    lines.append("[NON-CONSENTED REGION REDACTED]")
                    redaction_inserted = True
                continue
            if in_nonconsented_region:
                continue
            lines.append(line)
        return "\n".join(lines)

    def _line_has_credential_signal(self, normalized_line: str) -> bool:
        return bool(
            self._CREDENTIAL_SIGNAL_RE.search(normalized_line)
            and (self._CREDENTIAL_RE.search(normalized_line) or self._CREDENTIAL_VALUE_RE.search(normalized_line))
        )

    def _normalize_for_detection(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text)
        return normalized.translate(self._CONFUSABLES)
