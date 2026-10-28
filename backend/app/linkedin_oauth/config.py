"""Configuracion segura de LinkedIn OAuth para CloudEdTech."""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BACKEND_DIR / ".env")


@dataclass(frozen=True)
class LinkedInOAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: tuple[str, ...]


def cargar_configuracion() -> LinkedInOAuthConfig:
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "").strip()
    scopes = tuple(
        valor
        for valor in os.getenv(
            "LINKEDIN_SCOPES", "w_member_social"
        ).split()
        if valor
    )

    if not client_id or not client_secret:
        raise ValueError(
            "Faltan credenciales de LinkedIn en el backend."
        )

    url = urlparse(redirect_uri)

    if (
        (
        url.scheme != "https"
        and not (
            url.scheme == "http"
            and url.hostname in ("localhost", "127.0.0.1")
            and url.port == 5174
        )
    )
        or not url.netloc
        or url.username is not None
        or url.password is not None
        or url.query
        or url.fragment
    ):
        raise ValueError(
            "LINKEDIN_REDIRECT_URI debe ser una URL HTTPS valida."
        )

    if not scopes or "w_member_social" not in scopes:
        raise ValueError(
            "Falta el permiso w_member_social."
        )

    return LinkedInOAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes,
    )
