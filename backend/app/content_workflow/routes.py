from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from fastapi.responses import FileResponse
from typing import Literal

from app.content_workflow.brand_images import generar_pieza_corporativa

from typing import Literal
from app.users.models import User
from urllib.parse import quote
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.content_workflow.schemas import (
    CrearContenidoRequest,
    RevisarContenidoRequest,
)
from app.content_workflow.service import solicitar_motor
from app.security.dependencies import require_role


router = APIRouter(
    prefix="/api/v1/content-workflow",
    tags=["Content Workflow"],
    dependencies=[Depends(require_role("admin", "community_manager"))],
)


class GenerarRespuestaQuejaRequest(BaseModel):
    interaccion_id: int = Field(gt=0)


class RegenerarContenidoRequest(BaseModel):
    texto: str = Field(min_length=1, max_length=10000)
    canal: str = Field(min_length=1, max_length=150)
    formato: str
    tono: str = "profesional"



class EvaluarAlineacionMarcaRequest(BaseModel):
    contenido: str
    plataforma: Literal["linkedin", "x", "discord"]
    origen: str = ""
    contenido_id: int | None = Field(default=None, gt=0)


@router.post("/brand-alignment")
def evaluar_alineacion_marca_contenido(
    solicitud: EvaluarAlineacionMarcaRequest,
):
    return solicitar_motor(
        "POST",
        "/api/content/brand-alignment",
        datos=solicitud.model_dump(),
    )


class ConfirmarAlineacionMarcaRequest(BaseModel):
    contenido_id: int = Field(gt=0)
    contenido: str = Field(min_length=1)
    plataforma: Literal["linkedin", "x", "discord"]
    evaluacion: dict


@router.post("/brand-alignment/commit")
def confirmar_alineacion_marca(solicitud: ConfirmarAlineacionMarcaRequest):
    return solicitar_motor(
        "POST", "/api/content/brand-alignment/commit", datos=solicitud.model_dump()
    )




class GenerarContenidoOriginalRequest(BaseModel):
    tema: str = Field(min_length=1, max_length=150)
    instrucciones: str = Field(default="", max_length=2000)
    formato: Literal["linkedin", "x", "discord"]
    tono: str = Field(default="profesional", max_length=80)



@router.post("/messages/{interaccion_id}/analyze")
def analizar_mensaje_individual(interaccion_id: int):
    """Solicita al Motor IA el analisis de una interaccion."""
    from fastapi import HTTPException

    if interaccion_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="Identificador de interaccion invalido.",
        )

    return solicitar_motor(
        "POST",
        f"/api/community/messages/{interaccion_id}/analyze",
    )


@router.post("/generate-original")
def generar_contenido_original(solicitud: GenerarContenidoOriginalRequest):
    return solicitar_motor(
        "POST",
        "/api/content/generate-original",
        datos=solicitud.model_dump(),
    )

@router.post("/regenerate")
def regenerar_contenido(solicitud: RegenerarContenidoRequest):
    from fastapi import HTTPException

    if solicitud.formato not in {"linkedin", "x", "discord"}:
        raise HTTPException(
            status_code=422,
            detail="Formato no disponible para regeneracion",
        )

    return solicitar_motor(
        "POST",
        "/api/content/generate",
        solicitud.model_dump(),
    )


@router.post("/drafts")
def guardar_borrador(solicitud: CrearContenidoRequest):
    return solicitar_motor(
        "POST",
        "/api/content/drafts",
        solicitud.model_dump(),
    )


class ActualizarImagenBorradorRequest(BaseModel):
    imagen_generada_url: str | None = None


@router.patch("/drafts/{contenido_id}/image")
def actualizar_imagen_borrador(
    contenido_id: int,
    solicitud: ActualizarImagenBorradorRequest,
):
    from fastapi import HTTPException

    if contenido_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="El identificador debe ser positivo.",
        )

    return solicitar_motor(
        "PATCH",
        f"/api/content/{contenido_id}/image",
        solicitud.model_dump(),
    )


@router.post("/complaints/generate-response")
def generar_respuesta_queja(
    solicitud: GenerarRespuestaQuejaRequest,
):
    return solicitar_motor(
        "POST",
        "/api/community/complaints/generate-response",
        solicitud.model_dump(),
    )


@router.patch("/{contenido_id}/status")
def revisar_contenido(
    contenido_id: int,
    solicitud: RevisarContenidoRequest,
):
    if contenido_id <= 0:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail="El identificador debe ser positivo",
        )

    return solicitar_motor(
        "PATCH",
        f"/api/content/{contenido_id}/status",
        solicitud.model_dump(),
    )



class ActualizarCuraduriaRequest(BaseModel):
    status: str

    @classmethod
    def _estados_permitidos(cls):
        return {"pending", "curated", "discarded"}


@router.patch("/messages/{interaccion_id}/curation")
def actualizar_curaduria_mensaje(
    interaccion_id: int,
    solicitud: ActualizarCuraduriaRequest,
):
    from fastapi import HTTPException

    if interaccion_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="El identificador debe ser positivo",
        )

    if solicitud.status not in ActualizarCuraduriaRequest._estados_permitidos():
        raise HTTPException(
            status_code=422,
            detail="Estado de curaduria no valido",
        )

    return solicitar_motor(
        "PATCH",
        f"/api/community/messages/{interaccion_id}/curation",
        solicitud.model_dump(),
    )


class ActualizarEtapaFlujoRequest(BaseModel):
    stage: str


@router.patch("/messages/{interaccion_id}/workflow")
def actualizar_etapa_mensaje(
    interaccion_id: int,
    solicitud: ActualizarEtapaFlujoRequest,
):
    from fastapi import HTTPException

    if interaccion_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="El identificador debe ser positivo",
        )

    etapas_permitidas = {
        "en_analisis",
        "en_redaccion",
        "en_aprobacion",
    }

    if solicitud.stage not in etapas_permitidas:
        raise HTTPException(
            status_code=422,
            detail="Etapa de flujo no valida",
        )

    return solicitar_motor(
        "PATCH",
        f"/api/community/messages/{interaccion_id}/workflow",
        solicitud.model_dump(),
    )

class PublicarContenidoDiscordRequest(BaseModel):
    canal_id: str = Field(min_length=1, max_length=30)
    modo: Literal["publicacion", "respuesta"] = "publicacion"
    mensaje_original_id: str | None = None
    tipo_contenido: Literal["texto", "texto_imagen", "imagen"] = "texto"



@router.get("/messages/{interaccion_id}/origin")
def consultar_origen_interaccion(
    interaccion_id: int,
    usuario: User = Depends(require_role("admin", "community_manager")),
):
    from fastapi import HTTPException

    if interaccion_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="Identificador de interaccion invalido.",
        )

    return solicitar_motor(
        "GET",
        f"/api/community/messages/{interaccion_id}",
    )



@router.get("/discord/recovery-preview")
def consultar_mensajes_discord_para_recuperar(
    canal_id: str = "",
    buscar: str = "",
    dias: int | None = 7,
    solo_pendientes: bool = True,
    pagina: int = 1,
):
    """Vista previa protegida, sin guardar mensajes."""
    from fastapi import HTTPException

    if pagina < 1 or len(buscar) > 200:
        raise HTTPException(
            status_code=422,
            detail="Filtros de consulta invalidos.",
        )

    if dias is not None and dias not in (1, 7, 30):
        raise HTTPException(
            status_code=422,
            detail="Periodo de consulta invalido.",
        )

    parametros = [
        f"canal_id={canal_id}",
        f"buscar={quote(buscar, safe='')}",
        f"solo_pendientes={str(solo_pendientes).lower()}",
        f"pagina={pagina}",
    ]

    if dias is not None:
        parametros.append(f"dias={dias}")

    return solicitar_motor(
        "GET",
        "/api/community/discord/recovery-preview?"
        + "&".join(parametros),
    )


class MensajeDiscordSeleccionadoRequest(BaseModel):
    channel_id: str = Field(pattern=r"^\d{15,22}$")
    message_id: str = Field(pattern=r"^\d{15,22}$")


class RecuperarMensajesDiscordRequest(BaseModel):
    mensajes: list[MensajeDiscordSeleccionadoRequest] = Field(
        min_length=1,
        max_length=20,
    )


@router.post("/discord/recover-selected")
def recuperar_mensajes_discord(
    solicitud: RecuperarMensajesDiscordRequest,
):
    """Envia al Motor IA los mensajes historicos seleccionados."""
    return solicitar_motor(
        "POST",
        "/api/community/discord/recover-selected",
        solicitud.model_dump(),
    )

@router.get("/discord-channels")
def consultar_canales_discord():
    return solicitar_motor(
        "GET",
        "/api/content/discord-channels",
    )


@router.post("/{contenido_id}/publish")
def publicar_contenido_aprobado(
    contenido_id: int,
    solicitud: PublicarContenidoDiscordRequest,
):
    from fastapi import HTTPException

    if contenido_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="Identificador de contenido invalido",
        )

    datos = solicitud.model_dump()

    if solicitud.tipo_contenido != "texto":
        import base64
        import mimetypes
        import re

        referencia = solicitar_motor(
            "GET",
            f"/api/content/{contenido_id}/publication-image",
        )

        imagen_url = referencia.get("imagen_generada_url")
        prefijo = "/api/v1/content-workflow/corporate-images/"

        if not isinstance(imagen_url, str) or not imagen_url.startswith(prefijo):
            raise HTTPException(
                status_code=422,
                detail="El contenido aprobado no tiene imagen asociada.",
            )

        imagen_id = imagen_url[len(prefijo):]

        if re.fullmatch(r"[a-f0-9]{32}", imagen_id) is None:
            raise HTTPException(
                status_code=422,
                detail="Referencia de imagen corporativa invalida.",
            )

        imagen_path = _corporate_image_dir() / f"{imagen_id}.png"

        if not imagen_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="No se encontro la imagen aprobada.",
            )

        imagen_bytes = imagen_path.read_bytes()

        if not imagen_bytes:
            raise HTTPException(
                status_code=422,
                detail="La imagen aprobada esta vacia.",
            )

        datos["imagen_base64"] = base64.b64encode(
            imagen_bytes
        ).decode("ascii")
        datos["imagen_nombre"] = imagen_path.name
        datos["imagen_mime"] = (
            mimetypes.guess_type(imagen_path.name)[0]
            or "application/octet-stream"
        )

    return solicitar_motor(
        "POST",
        f"/api/content/{contenido_id}/publish",
        datos,
    )


from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.audit.service import create_audit_log
from app.database.dependencies import get_db


class ConfirmacionManualRequest(BaseModel):
    url_publicacion: str = Field(min_length=1, max_length=2048)


@router.post("/{contenido_id}/confirm-manual-publication")
def confirmar_publicacion_manual_administrativa(
    contenido_id: int,
    solicitud: ConfirmacionManualRequest,
    usuario: User = Depends(require_role("admin", "community_manager")),
    db: Session = Depends(get_db),
):
    if contenido_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="Identificador de contenido invalido",
        )

    resultado = solicitar_motor(
        "POST",
        f"/api/content/{contenido_id}/confirm-manual-publication",
        {
            "url_publicacion": solicitud.url_publicacion,
            "responsable": usuario.username,
        },
    )

    create_audit_log(
        db=db,
        action="manual_publication_confirmed",
        resource_type="content",
        user_id=usuario.id,
        resource_id=str(contenido_id),
        details=(
            f"Plataforma: {resultado.get('plataforma')}; "
            f"URL: {resultado.get('url_publicacion')}"
        ),
    )

    return resultado


# CLOUDedTECH_READ_ONLY_MOTOR_ROUTES
# Consultas autenticadas al Motor IA; no publican contenido.

@router.get("/dashboard")
def consultar_dashboard_motor():
    return solicitar_motor("GET", "/api/community/dashboard")


@router.get("/analytics")
def consultar_analytics_motor():
    return solicitar_motor("GET", "/api/community/analytics")


@router.get("/messages")
def consultar_mensajes_motor(limit: int | None = None):
    if limit is not None:
        if limit < 1 or limit > 500:
            raise HTTPException(
                status_code=422,
                detail="El parametro limit debe estar entre 1 y 500",
            )
        return solicitar_motor("GET", f"/api/community/messages?limite={limit}")

    return solicitar_motor("GET", "/api/community/messages")


@router.get("/complaints")
def consultar_quejas_motor():
    return solicitar_motor("GET", "/api/community/complaints")


@router.get("/content")
def consultar_contenidos_motor():
    return solicitar_motor("GET", "/api/content")


class CorporateImageRequest(BaseModel):
    plataforma: Literal["linkedin", "x", "discord"]
    titulo: str = Field(min_length=1, max_length=65)
    mensaje: str = Field(min_length=1, max_length=2000)


def _corporate_image_dir() -> Path:
    import os

    configured = os.getenv("CLOUDEDTECH_IMAGE_DIR", "").strip()

    if configured:
        directory = Path(configured).expanduser()

        if not directory.is_absolute():
            raise RuntimeError(
                "CLOUDEDTECH_IMAGE_DIR must be an absolute path"
            )

        return directory

    return (
        Path(__file__).resolve().parents[2]
        / "generated_content_images"
    )


@router.post("/corporate-images")
def create_corporate_image(solicitud: CorporateImageRequest):
    _corporate_image_dir().mkdir(
        parents=True,
        exist_ok=True,
    )

    image_id = uuid4().hex
    destination = _corporate_image_dir() / f"{image_id}.png"

    generar_pieza_corporativa(
        plataforma=solicitud.plataforma,
        titulo=solicitud.titulo,
        mensaje=solicitud.mensaje,
        destino=destination,
    )

    return {
        "image_id": image_id,
        "image_url": (
            f"/api/v1/content-workflow/corporate-images/{image_id}"
        ),
        "platform": solicitud.plataforma,
        "generator": "corporate_template",
    }


@router.get("/corporate-images/{image_id}")
def get_corporate_image(image_id: str):
    if (
        len(image_id) != 32
        or any(character not in "0123456789abcdef" for character in image_id)
    ):
        raise HTTPException(status_code=404, detail="Image not found")

    image_path = _corporate_image_dir() / f"{image_id}.png"

    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(
        image_path,
        media_type="image/png",
        filename="cloudedtech-corporate.png",
    )


# ------------------------------------------------------------
# Administrative control for the simulated community.
# Admin-only, with audit entries for effective state changes.
# No background generator is started by these routes.
# ------------------------------------------------------------

from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.audit.service import create_audit_log


class SolicitudSimulacionAdministrativa(BaseModel):
    tema: Literal[
        "ia",
        "programacion",
        "ciberseguridad",
        "datos",
        "mixto",
    ] = "mixto"
    ritmo: Literal[
        "bajo",
        "medio",
        "alto",
    ] = "medio"


@router.get("/simulation/status")
def consultar_estado_simulacion_administrativa(
    current_user: User = Depends(require_role("admin")),
):
    return solicitar_motor(
        "GET",
        "/api/community/simulation/status",
    )


@router.post("/simulation/start")
def iniciar_simulacion_administrativa(
    solicitud: SolicitudSimulacionAdministrativa,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    resultado = solicitar_motor(
        "POST",
        "/api/community/simulation/start",
        datos=solicitud.model_dump(),
    )

    if resultado.get("cambio_realizado") is True:
        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="SIMULATION_STARTED",
            resource_type="community_simulation",
            resource_id="discord_demo",
            details=(
                "tema=" + solicitud.tema
                + ";ritmo=" + solicitud.ritmo
                + ";publicar_discord=false"
            ),
        )

    return resultado


@router.post("/simulation/stop")
def detener_simulacion_administrativa(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    resultado = solicitar_motor(
        "POST",
        "/api/community/simulation/stop",
    )

    if resultado.get("cambio_realizado") is True:
        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="SIMULATION_STOPPED",
            resource_type="community_simulation",
            resource_id="discord_demo",
            details="publicar_discord=false",
        )

    return resultado



# PARTICIPANTES DEMO ADMINISTRATIVOS - PASO 3161

class CrearParticipanteDemoAdmin(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    avatar_url: str | None = None


class ActualizarParticipanteDemoAdmin(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    activo: bool | None = None
    avatar_url: str | None = None


def verificar_simulacion_detenida():
    estado = solicitar_motor(
        "GET",
        "/api/community/simulation/status",
    )

    if estado.get("estado") != "detenido" or estado.get("generador_activo"):
        raise HTTPException(
            status_code=409,
            detail="Detenga la simulacion antes de modificar participantes.",
        )


@router.get("/simulation/participants")
def listar_participantes_administrativos(
    current_user: User = Depends(require_role("admin")),
):
    return solicitar_motor(
        "GET",
        "/api/community/simulation/participants",
    )


@router.post("/simulation/participants")
def crear_participante_administrativo(
    solicitud: CrearParticipanteDemoAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    verificar_simulacion_detenida()

    resultado = solicitar_motor(
        "POST",
        "/api/community/simulation/participants",
        datos=solicitud.model_dump(),
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="SIMULATION_PARTICIPANT_CREATED",
        resource_type="community_simulation_participant",
        resource_id=str(resultado.get("id", "")),
        details="Participante virtual creado",
    )

    return resultado


@router.patch("/simulation/participants/{participante_id}")
def actualizar_participante_administrativo(
    participante_id: str,
    solicitud: ActualizarParticipanteDemoAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    verificar_simulacion_detenida()

    resultado = solicitar_motor(
        "PATCH",
        f"/api/community/simulation/participants/{participante_id}",
        datos=solicitud.model_dump(exclude_unset=True),
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="SIMULATION_PARTICIPANT_UPDATED",
        resource_type="community_simulation_participant",
        resource_id=participante_id,
        details="Perfil o estado de participante actualizado",
    )

    return resultado


@router.delete("/simulation/participants/{participante_id}")
def eliminar_participante_administrativo(
    participante_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    verificar_simulacion_detenida()

    resultado = solicitar_motor(
        "DELETE",
        f"/api/community/simulation/participants/{participante_id}",
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="SIMULATION_PARTICIPANT_DELETED",
        resource_type="community_simulation_participant",
        resource_id=participante_id,
        details="Participante retirado de futuras simulaciones",
    )

    return resultado


# Consulta protegida de la configuracion efectiva del Motor IA.
@router.get("/ai-settings")
def consultar_configuracion_ia():
    return solicitar_motor(
        "GET",
        "/api/content/ai-settings",
    )


# Registro administrativo de borradores educativos.
class CrearPublicacionEducativaAdminRequest(BaseModel):
    tema: Literal[
        "api",
        "python",
        "sql",
        "inteligencia artificial",
        "docker",
        "postgresql",
        "ciberseguridad",
        "react",
    ]
    titulo: str = Field(min_length=1, max_length=200)
    contenido: str = Field(min_length=1, max_length=10000)


@router.post("/educational/publications")
def crear_publicacion_educativa_admin(
    solicitud: CrearPublicacionEducativaAdminRequest,
    usuario: User = Depends(require_role("admin", "community_manager")),
):
    return solicitar_motor(
        "POST",
        "/api/educational/publications",
        datos={
            **solicitud.model_dump(),
            "responsable": usuario.username,
        },
    )

# CONFIGURACION ADMINISTRATIVA DISCORD - PASO 3181

class ActualizarDiscordDemoAdmin(BaseModel):
    habilitado: bool | None = None
    canal: Literal["general", "faq", "pqrs", "notificaciones", "chat-egresados", "oportunidades-laborales", "foro-educativo"] | None = None
    canales: list[Literal["general", "faq", "pqrs", "notificaciones", "chat-egresados", "oportunidades-laborales", "foro-educativo"]] | None = None


@router.get("/simulation/discord/config")
def consultar_discord_demo_administrativo(
    current_user: User = Depends(require_role("admin")),
):
    return solicitar_motor(
        "GET",
        "/api/community/simulation/discord/config",
    )


@router.patch("/simulation/discord/config")
def actualizar_discord_demo_administrativo(
    solicitud: ActualizarDiscordDemoAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    verificar_simulacion_detenida()

    cambios = solicitud.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=422,
            detail="Debe indicar al menos un cambio.",
        )

    anterior = solicitar_motor(
        "GET",
        "/api/community/simulation/discord/config",
    )

    resultado = solicitar_motor(
        "PATCH",
        "/api/community/simulation/discord/config",
        datos=cambios,
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="SIMULATION_DISCORD_CONFIG_UPDATED",
        resource_type="community_simulation_discord",
        resource_id="1562138935948353588",
        details=(
            f"Discord habilitado: "
            f"{anterior.get('habilitado')} -> "
            f"{resultado.get('habilitado')}; "
            f"canales: {anterior.get('canales', [anterior.get('canal')])} -> "
            f"{resultado.get('canales', [resultado.get('canal')])}"
        ),
    )

    return resultado
