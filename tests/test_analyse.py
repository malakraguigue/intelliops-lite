
import unittest

from src.analyse import (
    analyser,
    classifier,
    compter_erreurs,
    est_doublon,
    chercher_procedures,
)
from src.contrat import PROCEDURES, Evenement


def evt(
    type_="LOG",
    severity="HIGH",
    message="OOMKilled restarts=14",
    composant="backend",
):
    return Evenement(
        "EVT-00001",
        "2026-10-05T10:00:00Z",
        "DOCKER",
        composant,
        "production",
        type_,
        severity,
        message,
    )


class TestAnalyse(unittest.TestCase):

    def test_doublon(self):
        vus = set()
        self.assertFalse(est_doublon(evt(), vus))
        self.assertTrue(est_doublon(evt(), vus))

    def test_doublon_timestamp_different(self):
        vus = set()
        premier = evt()
        second = evt()
        second.timestamp = "2026-10-05T10:00:01Z"

        self.assertFalse(est_doublon(premier, vus))
        self.assertFalse(est_doublon(second, vus))

    def test_compter_erreurs(self):
        compteur = {}
        self.assertEqual(compter_erreurs(evt(), compteur), 1)
        self.assertEqual(compter_erreurs(evt(), compteur), 2)
        self.assertEqual(compteur["backend"], 2)

    def test_compter_evenement_non_erreur(self):
        compteur = {}
        e = evt(severity="LOW")
        self.assertEqual(compter_erreurs(e, compteur), 0)
        self.assertEqual(compteur, {})

    def test_chercher_procedures(self):
        resultats = chercher_procedures(evt(), PROCEDURES)
        self.assertEqual(len(resultats), 1)
        self.assertIn("memoire", resultats[0])

    def test_classifier_boucle(self):
        e = evt()
        self.assertEqual(classifier(e, 3), "CRITICAL")
        self.assertEqual(classifier(e, 2), "HIGH")

    def test_analyser_erreur_critique(self):
        e = evt()
        resultat = analyser(e, PROCEDURES, 3)

        self.assertEqual(resultat.level, "CRITICAL")
        self.assertEqual(resultat.action, "Redemarrer le service backend")
        self.assertTrue(resultat.sensitive)
        self.assertEqual(e.status, "ANALYZED")

    def test_analyser_vulnerabilite(self):
        e = evt(
            type_="VULNERABILITY",
            severity="HIGH",
            composant="lib-xyz",
        )
        resultat = analyser(e, PROCEDURES)

        self.assertEqual(
            resultat.action,
            "Mettre a jour la dependance lib-xyz",
        )
        self.assertFalse(resultat.sensitive)

    def test_analyser_pipeline(self):
        e = evt(
            type_="PIPELINE_FAILURE",
            severity="HIGH",
            composant="build",
        )
        resultat = analyser(e, PROCEDURES)

        self.assertEqual(resultat.action, "Relancer le pipeline build")
        self.assertEqual(resultat.sources, ["DOCKER"])


if __name__ == "__main__":
    unittest.main()
