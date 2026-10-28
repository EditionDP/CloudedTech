"""Rutas OAuth de LinkedIn para CloudEdTech."""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.linkedin_oauth.config import cargar_configuracion
from app.linkedin_oauth.state import crear_state, consumir_state
from app.linkedin_oauth.token_exchange import (
    LinkedInTokenExchangeError,
    intercambiar_codigo,
)
from app.linkedin_oauth.token_store import guardar_token
from app.security.dependencies import require_role
from app.users.models import User


router = APIRouter(
    prefix="/api/v1/linkedin/oauth",
    tags=["LinkedIn OAuth"],
)


class LinkedInAuthorizationResponse(BaseModel):
    authorization_url: str
    expires_in_seconds: int


@router.get(
    "/start",
    response_model=LinkedInAuthorizationResponse,
)
def iniciar_autorizacion_linkedin(
    current_user: User = Depends(
        require_role("admin", "community_manager")
    ),
):
    try:
        config = cargar_configuracion()
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="La conexion de LinkedIn aun no esta configurada.",
        )

    state = crear_state(current_user.id)

    parametros = {
        "response_type": "code",
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "state": state,
        "scope": " ".join(config.scopes),
    }

    authorization_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        + urlencode(parametros)
    )

    return LinkedInAuthorizationResponse(
        authorization_url=authorization_url,
        expires_in_seconds=600,
    )



class LinkedInCompleteRequest(BaseModel):
    code: str
    state: str


class LinkedInCompleteResponse(BaseModel):
    status: str
    message: str


@router.post(
    "/complete",
    response_model=LinkedInCompleteResponse,
)
def completar_autorizacion_linkedin(
    payload: LinkedInCompleteRequest,
    current_user: User = Depends(
        require_role("admin", "community_manager")
    ),
):
    if not payload.code.strip() or not payload.state.strip():
        raise HTTPException(
            status_code=400,
            detail="Codigo OAuth o state invalido.",
        )

    if not consumir_state(payload.state, current_user.id):
        raise HTTPException(
            status_code=400,
            detail="La autorizacion OAuth no es valida o ha vencido.",
        )

    try:
        resultado = intercambiar_codigo(payload.code)
    except LinkedInTokenExchangeError:
        raise HTTPException(
            status_code=502,
            detail="No fue posible completar la autorizacion con LinkedIn.",
        )

    try:
        guardar_token(
            user_id=current_user.id,
            access_token=resultado.access_token,
            expires_in=resultado.expires_in,
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="No fue posible guardar la conexion de LinkedIn.",
        )

    return LinkedInCompleteResponse(
        status="conectado",
        message="Cuenta de LinkedIn conectada correctamente.",
    )


class LinkedInProfileResponse(BaseModel):
    status: str
    author_urn: str


@router.get(
    "/profile",
    response_model=LinkedInProfileResponse,
)
def consultar_perfil_linkedin(
    current_user: User = Depends(
        require_role("admin", "community_manager")
    ),
):
    """Consulta el perfil autorizado sin exponer credenciales."""
    from app.linkedin_oauth.profile import (
        LinkedInProfileError,
        obtener_perfil_linkedin,
    )

    try:
        perfil = obtener_perfil_linkedin(current_user.id)
    except LinkedInProfileError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return LinkedInProfileResponse(
        status="conectado",
        author_urn=perfil.author_urn,
    )

from typing import Literal
from app.linkedin_oauth.publication_service import publicar_contenido_linkedin


class LinkedInPublishRequest(BaseModel):
    tipo_contenido: Literal["texto", "texto_imagen", "imagen"]


@router.post("/publish/{contenido_id}")
def publicar_aprobacion_linkedin(
    contenido_id: int,
    solicitud: LinkedInPublishRequest,
    current_user: User = Depends(
        require_role("admin", "community_manager")
    ),
):
    return publicar_contenido_linkedin(
        contenido_id=contenido_id,
        user_id=current_user.id,
        tipo_contenido=solicitud.tipo_contenido,
    )

