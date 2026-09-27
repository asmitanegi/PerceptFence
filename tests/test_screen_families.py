"""Tests for the v0.4 rendered-screen redaction families (T7-T10).

All secret-shaped strings are assembled at runtime from fragments so no
provider-format literal appears in the repository.
"""

import unittest

from screenshare_mediator.capture import SyntheticCaptureAdapter
from screenshare_mediator.models import PolicyDecision
from screenshare_mediator.redaction import RedactionEngine

_A = "ABCDEFGHJKLMNPQRSTUVWXYZ234567"


def _mediate(text: str, screen_families: bool = True) -> str:
    fixture = {"id": "t", "scenario_class": "terminal_secret", "modality": ["screen_text"],
               "input": {"window_title": "", "visible_text": text}}
    cap = SyntheticCaptureAdapter().capture(fixture)
    dec = PolicyDecision("t", "terminal_secret", "redact_before_model", "test")
    return RedactionEngine(screen_families=screen_families).mediate(cap, dec).model_context


class ScreenFamilyTests(unittest.TestCase):
    def test_t7_assignment_redacts_value(self):
        # Note: the v0.3 orphan-credential family also replaces the variable NAME
        # (e.g. AWS_SECRET_ACCESS_KEY -> [REDACTED CREDENTIAL]); the frozen v0.4
        # engine keeps that behaviour, so only non-secret-named keys stay readable.
        value = "vp4Egj " + "Alzyyfg9LkdhJ0jm" + "ONFjDXEZxex8fRTg09"  # OCR split the value
        out = _mediate("AWS_" + "SECRET_ACCESS_KEY=" + value + "\nAWS_DEFAULT_REGION=us-west-2")
        self.assertNotIn("Alzyyfg9", out)
        self.assertNotIn("vp4Egj", out)
        self.assertIn("AWS_DEFAULT_REGION=us-west-2", out)

    def test_t8_provider_token_with_ocr_split_is_redacted(self):
        tok = "gh" + "p_" + "ygQWJoj" + " " + "GnAtFKebmokgDb9Hg3KYWSIA2mOC"
        out = _mediate("git clone https://github.com/acme/x.git # " + tok)
        self.assertNotIn("ygQWJoj", out)
        self.assertNotIn("GnAtFKebmokgDb9", out)
        self.assertIn("git clone", out)

    def test_t8_aws_key_id_bare(self):
        key = "AK" + "IA" + (_A * 2)[:16]
        out = _mediate("found " + key + " in logs")
        self.assertNotIn(key, out)

    def test_t8_pem_block(self):
        body = "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW"
        out = _mediate("-----BEGIN OPENSSH " + "PRIVATE KEY-----\n" + body + "\n-----END OPENSSH " + "PRIVATE KEY-----")
        self.assertNotIn(body[:30], out)

    def test_t9_url_userinfo_password_only(self):
        out = _mediate("DATABASE_URL_HOST postgres: //app_user: vper6s7gjq%nj@db.internal:5432/orders")
        self.assertNotIn("vper6s7gjq", out)
        self.assertIn("5432/orders", out)

    def test_t10_phone_email_card_and_labels(self):
        out = _mediate("Email oah tanaka @example.com\nPhone (830) 555-0184\n"
                       "Card on fle 4548 3406 8152 7789\nCustomer Noah Tanaka\nStatus Refund pending")
        for leaked in ("555-0184", "tanaka @example.com", "4548 3406", "Noah Tanaka"):
            self.assertNotIn(leaked, out)
        self.assertIn("Refund pending", out)

    def test_benign_developer_text_survives(self):
        text = ("ModuleNotFoundError: No module named 'psycopg2'\nHTTP/1.1 502 Bad Gateway\n"
                "Error: Process completed with exit code 22.\n3 failed, 41 passed in 2.31s\n"
                "AWS_DEFAULT_REGION=us-west-2\nFEATURE_CHECKOUT_V2=true\nOrder #45545")
        out = _mediate(text)
        for keep in ("psycopg2", "502 Bad Gateway", "exit code 22", "41 passed", "us-west-2",
                     "FEATURE_CHECKOUT_V2=true", "45545"):
            self.assertIn(keep, out)

    def test_screen_families_off_reproduces_v03(self):
        tok = "xo" + "xb-" + "123456789012-1234567890123-" + "abcdefghijklmnopqrstuvwx"
        self.assertIn("abcdefghijklmnop", _mediate("note " + tok, screen_families=False))
        self.assertNotIn("abcdefghijklmnop", _mediate("note " + tok, screen_families=True))


if __name__ == "__main__":
    unittest.main()
