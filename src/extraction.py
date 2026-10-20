import re

from src.contrat import Evenement

# nom=valeur ou nom: valeur ; la valeur s'arrete a un espace, &, , ou ;
_MOTIF_SECRET = re.compile(
    r"(password|passwd|token|secret|api_key|apikey)(\s*[=:]\s*)[^\s&,;]+",
    re.IGNORECASE,
)


def masquer_secrets(texte: str) -> str:
    return _MOTIF_SECRET.sub(r"\1\2[SECRET]", texte)


def normaliser_log(ligne: str, numero: int, source: str = "DOCKER",
                   environment: str = "production") -> Evenement:
    raise NotImplementedError


def normaliser_scan(rapport: dict, numero: int,
                    environment: str = "production") -> Evenement:
    raise NotImplementedError


def normaliser_pipeline(rapport: dict, numero: int,
                        environment: str = "production") -> Evenement:
    raise NotImplementedError