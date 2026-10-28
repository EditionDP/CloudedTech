"""Publicacion de texto en LinkedIn mediante Posts API."""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


LINKEDIN_POSTS_URL = "https://api.linkedin.com/rest/posts"
LINKEDIN_VERSION = "202610"


class LinkedInPublishError(Exception):
    """Error controlado de publicacion LinkedIn."""


class LinkedInResultUnknown(LinkedInPublishError):
    """No se puede determinar si LinkedIn recibio la publicacion."""


def publicar_texto_linkedin(
    *,
    access_token: str,
    author_urn: str,
    texto: str,
) -> str:
    """Publica texto y devuelve el identificador real de LinkedIn."""

    if not access_token or not access_token.strip():
        raise ValueError("No existe token OAuth de LinkedIn.")

    if not re.fullmatch(r"urn:li:person:[A-Za-z0-9_-]+", author_urn):
        raise ValueError("Perfil LinkedIn invalido.")

    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("El contenido no puede estar vacio.")

    payload = {
        "author": author_urn,
        "commentary": texto,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    solicitud = Request(
        LINKEDIN_POSTS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Linkedin-Version": LINKEDIN_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
        },
        method="POST",
    )

    try:
        with urlopen(solicitud, timeout=30) as respuesta:
            identificador = respuesta.headers.get("x-restli-id", "").strip()

            if not identificador.startswith(
                ("urn:li:share:", "urn:li:ugcPost:")
            ):
                raise LinkedInResultUnknown(
                    "LinkedIn respondio sin un identificador verificable."
                )

            return identificador

    except HTTPError as error:
        # No se reintenta automaticamente una solicitud de publicacion.
        raise LinkedInPublishError(
            f"LinkedIn rechazo la solicitud (HTTP {error.code})."
        ) from error

    except (URLError, TimeoutError, OSError) as error:
        raise LinkedInResultUnknown(
            "No se pudo determinar si LinkedIn recibio la publicacion."
        ) from error

def publicar_imagen_linkedin(
    *,
    access_token: str,
    author_urn: str,
    image_urn: str,
    texto: str = "",
) -> str:
    """Publica imagen, con texto opcional, y devuelve el URN del post."""

    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("No existe token OAuth de LinkedIn.")

    if not isinstance(author_urn, str) or not re.fullmatch(
        r"urn:li:person:[A-Za-z0-9_-]+", author_urn
    ):
        raise ValueError("Perfil LinkedIn invalido.")

    if not isinstance(image_urn, str) or not re.fullmatch(
        r"urn:li:image:[A-Za-z0-9_-]+", image_urn
    ):
        raise ValueError("Identificador de imagen LinkedIn invalido.")

    if not isinstance(texto, str):
        raise ValueError("El texto debe ser una cadena.")

    payload = {
        "author": author_urn,
        "commentary": texto,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "id": image_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    solicitud = Request(
        LINKEDIN_POSTS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Linkedin-Version": LINKEDIN_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
        },
        method="POST",
    )

    try:
        with urlopen(solicitud, timeout=30) as respuesta:
            identificador = respuesta.headers.get(
                "x-restli-id", ""
            ).strip()

            if not identificador.startswith(
                ("urn:li:share:", "urn:li:ugcPost:")
            ):
                raise LinkedInResultUnknown(
                    "LinkedIn respondio sin un identificador verificable."
                )

            return identificador

    except HTTPError as error:
        raise LinkedInPublishError(
            f"LinkedIn rechazo la publicacion con imagen (HTTP {error.code})."
        ) from error

    except (URLError, TimeoutError, OSError) as error:
        raise LinkedInResultUnknown(
            "No se pudo determinar si LinkedIn recibio la publicacion."
        ) from error