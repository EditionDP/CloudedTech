"""Identificacion del perfil LinkedIn mediante OpenID Connect."""

from dataclasses import dataclass

import httpx

from .token_store import obtener_token


USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


class LinkedInProfileError(Exception):
    """Error controlado al consultar el perfil LinkedIn."""


@dataclass(frozen=True)
class LinkedInProfile:
    member_id: str
    author_urn: str


def obtener_perfil_linkedin(user_id: int) -> LinkedInProfile:
    """Obtiene la identidad del perfil conectado sin exponer el token."""

    token = obtener_token(user_id)

    if not token:
        raise LinkedInProfileError(
            "No existe una conexion vigente con LinkedIn."
        )

    try:
        with httpx.Client(
            timeout=15.0,
            follow_redirects=False,
        ) as client:
            response = client.get(
                USERINFO_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
            )
    except httpx.HTTPError as exc:
        raise LinkedInProfileError(
            "No fue posible consultar el perfil de LinkedIn."
        ) from exc

    if response.status_code != 200:
        raise LinkedInProfileError(
            "LinkedIn no permitio consultar la identidad del perfil."
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise LinkedInProfileError(
            "LinkedIn devolvio una respuesta no valida."
        ) from exc

    if not isinstance(data, dict):
        raise LinkedInProfileError(
            "La respuesta del perfil no tiene el formato esperado."
        )

    member_id = data.get("sub")

    if (
        not isinstance(member_id, str)
        or not member_id
        or len(member_id) > 256
        or any(
            not (
                character.isascii()
                and (character.isalnum() or character in "_-")
            )
            for character in member_id
        )
    ):
        raise LinkedInProfileError(
            "LinkedIn no devolvio un identificador de perfil valido."
        )

    return LinkedInProfile(
        member_id=member_id,
        author_urn=f"urn:li:person:{member_id}",
    )