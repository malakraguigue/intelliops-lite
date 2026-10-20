import unittest

from src.extraction import masquer_secrets, normaliser_log

LIGNE = "2026-10-05 10:02:11 ERROR backend OOMKilled restarts=14 password=abc123"


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

    def test_normaliser_log(self):
        evt = normaliser_log(LIGNE, 42)
        self.assertEqual(evt.id, "EVT-00042")
        self.assertEqual(evt.timestamp, "2026-10-05T10:02:11Z")
        self.assertEqual(evt.source, "DOCKER")
        self.assertEqual(evt.environment, "production")
        self.assertEqual(evt.component, "backend")
        self.assertEqual(evt.event_type, "LOG")
        self.assertEqual(evt.severity, "HIGH")
        self.assertEqual(evt.message, "OOMKilled restarts=14 password=[SECRET]")
        self.assertNotIn("abc123", evt.message)

    def test_normaliser_log_severites(self):
        attendu = {"CRITICAL": "CRITICAL", "fatal": "CRITICAL",
                   "ERROR": "HIGH", "warn": "MEDIUM", "WARNING": "MEDIUM",
                   "INFO": "LOW", "DEBUG": "LOW"}
        for niveau, severite in attendu.items():
            ligne = f"2026-10-05 10:00:00 {niveau} api message test"
            self.assertEqual(normaliser_log(ligne, 1).severity, severite, niveau)

    def test_normaliser_log_parametres(self):
        evt = normaliser_log("2026-10-05 10:00:00 INFO api message", 7,
                             source="K8S", environment="dev")
        self.assertEqual(evt.source, "K8S")
        self.assertEqual(evt.environment, "dev")

    def test_normaliser_log_invalide(self):
        with self.assertRaises(ValueError):
            normaliser_log("2026-10-05 10:00:00 INFO backend", 1)


if __name__ == "__main__":
    unittest.main()