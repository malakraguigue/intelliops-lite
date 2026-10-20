import unittest

from src.contrat import Analyse, Evenement
from src.notification import (choisir_canal, notifier, rediger,
                              tracer_decision, valider_action)


def exemple(sensible=True, niveau="CRITICAL"):
    e = Evenement("EVT-00125", "2026-10-05T10:02:11Z", "DOCKER", "backend",
                  "production", "LOG", "HIGH", "OOMKilled restarts=14")
    a = Analyse("EVT-00125", niveau, "Manque de memoire",
                "Redemarrer le service backend", sensible, ["DOCKER"])
    return e, a


class TestNotification(unittest.TestCase):

    # --- choisir_canal ---
    def test_canaux(self):
        self.assertEqual(choisir_canal("CRITICAL"), "TEAMS")
        self.assertEqual(choisir_canal("HIGH"), "SLACK")
        self.assertEqual(choisir_canal("MEDIUM"), "EMAIL")
        self.assertEqual(choisir_canal("LOW"), "DASHBOARD")

    def test_canal_inconnu(self):
        with self.assertRaises(ValueError):
            choisir_canal("URGENT")

    # --- rediger ---
    def test_rediger(self):
        e, a = exemple()
        attendu = ("[CRITICAL] Composant : backend\n"
                   "Evenement : OOMKilled restarts=14\n"
                   "Explication : Manque de memoire\n"
                   "Action proposee : Redemarrer le service backend\n"
                   "Sources : DOCKER")
        self.assertEqual(rediger(e, a), attendu)

    def test_rediger_plusieurs_sources(self):
        e, a = exemple()
        a.sources = ["DOCKER", "CI"]
        self.assertTrue(rediger(e, a).endswith("Sources : DOCKER, CI"))

    # --- notifier ---
    def test_notifier(self):
        e, a = exemple()
        historique = []
        notif = notifier(e, a, historique)
        self.assertEqual(notif.event_id, "EVT-00125")
        self.assertEqual(notif.channel, "TEAMS")
        self.assertEqual(notif.recipient, "equipe-ops")
        self.assertEqual(notif.text, rediger(e, a))
        self.assertEqual(historique, [notif])
        self.assertEqual(e.status, "NOTIFIED")

    # --- valider_action ---
    def test_validation(self):
        _, a = exemple()
        self.assertTrue(valider_action(a, " OUI "))
        self.assertFalse(valider_action(a, "n"))

    def test_validation_reponses_acceptees(self):
        _, a = exemple()
        for reponse in ("o", "oui", "ok", "yes", "OK", " Yes "):
            self.assertTrue(valider_action(a, reponse), reponse)

    def test_validation_reponse_vide_refusee(self):
        _, a = exemple()
        self.assertFalse(valider_action(a, ""))

    def test_validation_action_non_sensible(self):
        _, a = exemple(sensible=False, niveau="LOW")
        self.assertTrue(valider_action(a, "n"))

    # --- tracer_decision ---
    def test_tracer_decision(self):
        _, a = exemple()
        journal = []
        entree = tracer_decision(a, True, "ops-oncall", journal,
                                 "2026-10-05T10:05:00Z")
        attendu = {"event_id": "EVT-00125",
                   "action": "Redemarrer le service backend",
                   "approved": True, "actor": "ops-oncall",
                   "timestamp": "2026-10-05T10:05:00Z"}
        self.assertEqual(entree, attendu)
        self.assertEqual(journal, [attendu])


if __name__ == "__main__":
    unittest.main()