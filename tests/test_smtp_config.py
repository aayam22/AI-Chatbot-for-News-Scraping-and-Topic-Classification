import os
import sys
import unittest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.app_server import normalize_smtp_password


class SmtpConfigTests(unittest.TestCase):
    def test_grouped_gmail_app_password_is_collapsed(self):
        self.assertEqual(
            normalize_smtp_password("abcd efgh ijkl mnop"),
            "abcdefghijklmnop",
        )

    def test_regular_password_is_only_trimmed(self):
        self.assertEqual(
            normalize_smtp_password("  not-a-grouped-password  "),
            "not-a-grouped-password",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
