"""Intercambio seguro de codigos OAuth de LinkedIn."""

from dataclasses import dataclass

import httpx

from app.linkedin_oauth.config import cargar_configuracion


TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


class LinkedInTokenExchangeError(Exception):
    """Error controlado durante el intercambio OAuth."""


@dataclass(frozen=True)
class LinkedInTokenResult:
    access_token: str
    expires_in: int


def intercambiar_codigo(code: str) -> LinkedInTokenResult:
    if not code or not code.strip():
        raise LinkedInTokenExchangeError(
            "No se recibio un codigo de autorizacion valido."
        )

    try:
        config = cargar_configuracion()
    except ValueError as exc:
        raise LinkedInTokenExchangeError(
            "La conexion de LinkedIn no esta configurada."
        ) from exc

    datos = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.redirect_uri,
        "client_id": config.client_id,
        "client_secret": config.client_secret,
    }

    try:
        with httpx.Client(
            timeout=15.0,
            follow_redirects=False,
        ) as cliente:
            respuesta = cliente.post(
                TOKEN_URL,
                data=datos,
                headers={
                    "Accept": "application/json",
                },
            )
    except httpx.RequestError as exc:
        raise LinkedInTokenExchangeError(
            "No fue posible contactar a LinkedIn."
        ) from exc

    if respuesta.status_code != 200:
        raise LinkedInTokenExchangeError(
            "LinkedIn rechazo el intercambio del codigo OAuth."
        )

    try:
        resultado = respuesta.json()
        token = resultado["access_token"]
        expiracion = int(resultado["expires_in"])

        if (
            not isinstance(token, str)
            or not token.strip()
            or expiracion <= 0
        ):
            raise ValueError("Respuesta OAuth invalida.")

    except (ValueError, TypeError, KeyError) as exc:
        raise LinkedInTokenExchangeError(
            "LinkedIn devolvio una respuesta OAuth invalida."
        ) from exc

    return LinkedInTokenResult(
        access_token=token,
        expires_in=expiracion,
    )
