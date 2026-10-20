import unittest

from src.extraction import (masquer_secrets, normaliser_log,
                            normaliser_pipeline, normaliser_scan)

LIGNE = "2026-10-05 10:02:11 ERROR backend OOMKilled restarts=14 password=abc123"


class TestExtraction(unittest.TestCase):

    # --- masquer_secrets ---
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

    # --- normaliser_log ---
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

    # --- normaliser_scan ---
    def test_normaliser_scan(self):
        rapport = {"cve": "CVE-2026-1234", "package": "lib-xyz",
                   "severity": "critical", "date": "2026-10-05T10:07:00Z"}
        evt = normaliser_scan(rapport, 8)
        self.assertEqual(evt.id, "EVT-00008")
        self.assertEqual(evt.source, "TRIVY")
        self.assertEqual(evt.component, "lib-xyz")
        self.assertEqual(evt.event_type, "VULNERABILITY")
        self.assertEqual(evt.timestamp, "2026-10-05T10:07:00Z")
        self.assertEqual(evt.severity, "CRITICAL")
        self.assertEqual(evt.message, "Vulnerabilite CVE-2026-1234 dans lib-xyz")

    def test_normaliser_scan_severite_inconnue(self):
        rapport = {"cve": "CVE-1", "package": "p", "severity": "unknown",
                   "date": "2026-10-05T10:07:00Z"}
        self.assertEqual(normaliser_scan(rapport, 1).severity, "LOW")

    def test_normaliser_scan_cle_manquante(self):
        with self.assertRaises(ValueError):
            normaliser_scan({"cve": "CVE-1", "package": "p", "date": "d"}, 1)

    # --- normaliser_pipeline ---
    def test_normaliser_pipeline_echec(self):
        rapport = {"job": "build", "status": "FAILED",
                   "date": "2026-10-05T10:06:00Z"}
        evt = normaliser_pipeline(rapport, 7)
        self.assertEqual(evt.source, "CI")
        self.assertEqual(evt.component, "build")
        self.assertEqual(evt.event_type, "PIPELINE_FAILURE")
        self.assertEqual(evt.severity, "HIGH")
        self.assertEqual(evt.message, "Pipeline build : FAILED")

    def test_normaliser_pipeline_ok(self):
        rapport = {"job": "test", "status": "success",
                   "date": "2026-10-05T10:06:00Z"}
        evt = normaliser_pipeline(rapport, 9)
        self.assertEqual(evt.event_type, "PIPELINE_OK")
        self.assertEqual(evt.severity, "LOW")

    def test_normaliser_pipeline_cle_manquante(self):
        with self.assertRaises(ValueError):
            normaliser_pipeline({"job": "build", "date": "d"}, 1)


if __name__ == "__main__":
    unittest.main()