from src.contrat import Analyse, Evenement, Notification

_CANAUX = {
    "CRITICAL": "TEAMS",
    "HIGH": "SLACK",
    "MEDIUM": "EMAIL",
    "LOW": "DASHBOARD",
}

_REPONSES_OUI = ("o", "oui", "ok", "yes")


def choisir_canal(niveau: str) -> str:
    if niveau not in _CANAUX:
        raise ValueError(f"Niveau inconnu : {niveau!r}")
    return _CANAUX[niveau]

def rediger(evt: Evenement, analyse: Analyse) -> str:
    raise NotImplementedError


def notifier(evt: Evenement, analyse: Analyse, historique: list) -> Notification:
    raise NotImplementedError


def valider_action(analyse: Analyse, reponse: str) -> bool:
    if not analyse.sensitive:
        return True
    return reponse.strip().lower() in _REPONSES_OUI


def tracer_decision(analyse: Analyse, approuve: bool, acteur: str,
                    journal: list, horodatage: str) -> dict:
    raise NotImplementedError