import unittest

from src.extraction import masquer_secrets


class TestExtraction(unittest.TestCase):
    def test_masquer_secrets(self):
        self.assertEqual(masquer_secrets("user=bob password=abc123"),
                         "user=bob password=[SECRET]")

    def test_masquer_secrets_casse_et_deux_points(self):
        self.assertEqual(masquer_secrets("TOKEN: xyz789"), "TOKEN: [SECRET]")

    def test_masquer_secrets_separateurs(self):
        self.assertEqual(masquer_secrets("token=abc&user=bob"),
                         "token=[SECRET]&user=bob")

    def test_masquer_secrets_sans_secret(self):
        self.assertEqual(masquer_secrets("Service demarre"), "Service demarre")


if __name__ == "__main__":
    unittest.main()