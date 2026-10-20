import re

from src.contrat import Evenement

# nom=valeur ou nom: valeur ; la valeur s'arrete a un espace, &, , ou ;
_MOTIF_SECRET = re.compile(
    r"(password|passwd|token|secret|api_key|apikey)(\s*[=:]\s*)[^\s&,;]+",
    re.IGNORECASE,
)
_SEVERITES_LOG = {
    "CRITICAL": "CRITICAL",
    "FATAL": "CRITICAL",
    "ERROR": "HIGH",
    "WARN": "MEDIUM",
    "WARNING": "MEDIUM",
}


def _identifiant(numero: int) -> str:
    return f"EVT-{numero:05d}"

def masquer_secrets(texte: str) -> str:
    return _MOTIF_SECRET.sub(r"\1\2[SECRET]", texte)


def normaliser_log(ligne: str, numero: int, source: str = "DOCKER",
                   environment: str = "production") -> Evenement:
    champs = ligne.split(maxsplit=4)
    if len(champs) < 5:
        raise ValueError(f"Ligne de log invalide (moins de 5 champs) : {ligne!r}")
    date, heure, niveau, composant, message = champs
    return Evenement(
        id=_identifiant(numero),
        timestamp=f"{date}T{heure}Z",
        source=source,
        component=composant,
        environment=environment,
        event_type="LOG",
        severity=_SEVERITES_LOG.get(niveau.upper(), "LOW"),
        message=masquer_secrets(message),
    )


def normaliser_scan(rapport: dict, numero: int,
                    environment: str = "production") -> Evenement:
    raise NotImplementedError


def normaliser_pipeline(rapport: dict, numero: int,
                        environment: str = "production") -> Evenement:
    raise NotImplementedError