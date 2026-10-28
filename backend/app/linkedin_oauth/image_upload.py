"""Carga controlada de imagenes PNG mediante LinkedIn Images API."""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.linkedin_oauth.publisher import (
    LINKEDIN_VERSION,
    LinkedInPublishError,
    LinkedInResultUnknown,
)


IMAGES_URL = "https://api.linkedin.com/rest/images?action=initializeUpload"
MAX_IMAGE_BYTES = 10 * 1024 * 1024


def cargar_imagen_linkedin(
    *,
    access_token: str,
    author_urn: str,
    imagen_png: bytes,
) -> str:
    """Carga un PNG y devuelve su URN para una publicacion LinkedIn."""

    if not access_token or not access_token.strip():
        raise ValueError("No existe token OAuth de LinkedIn.")

    if not re.fullmatch(r"urn:li:person:[A-Za-z0-9_-]+", author_urn):
        raise ValueError("Perfil LinkedIn invalido.")

    if not isinstance(imagen_png, bytes):
        raise ValueError("La imagen debe ser binaria.")

    if not imagen_png.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("La imagen corporativa no es un PNG valido.")

    if len(imagen_png) > MAX_IMAGE_BYTES:
        raise ValueError("La imagen supera el limite permitido.")

    solicitud = Request(
        IMAGES_URL,
        data=json.dumps({
            "initializeUploadRequest": {
                "owner": author_urn,
            }
        }).encode("utf-8"),
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
            datos = json.load(respuesta)

    except HTTPError as error:
        raise LinkedInPublishError(
            f"LinkedIn rechazo el registro de imagen (HTTP {error.code})."
        ) from error

    except (URLError, TimeoutError, OSError) as error:
        raise LinkedInResultUnknown(
            "No se pudo confirmar el registro de imagen."
        ) from error

    valor = datos.get("value", {})
    upload_url = valor.get("uploadUrl")
    image_urn = valor.get("image")

    if not isinstance(upload_url, str):
        raise LinkedInPublishError("LinkedIn no devolvio URL de carga.")

    if not isinstance(image_urn, str) or not image_urn.startswith(
        "urn:li:image:"
    ):
        raise LinkedInPublishError("LinkedIn no devolvio URN de imagen.")

    destino = urlparse(upload_url)

    if (
        destino.scheme != "https"
        or not destino.hostname
        or destino.username
        or destino.password
        or not (
            destino.hostname == "linkedin.com"
            or destino.hostname.endswith(".linkedin.com")
            or destino.hostname == "licdn.com"
            or destino.hostname.endswith(".licdn.com")
        )
    ):
        raise LinkedInPublishError(
            "LinkedIn devolvio una URL de carga no permitida."
        )

    carga = Request(
        upload_url,
        data=imagen_png,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "image/png",
        },
        method="PUT",
    )

    try:
        with urlopen(carga, timeout=60):
            pass

    except HTTPError as error:
        raise LinkedInPublishError(
            f"LinkedIn rechazo la carga PNG (HTTP {error.code})."
        ) from error

    except (URLError, TimeoutError, OSError) as error:
        raise LinkedInResultUnknown(
            "No se pudo confirmar la carga de imagen."
        ) from error

    return image_urn