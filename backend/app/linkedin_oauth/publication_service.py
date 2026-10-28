"""Orquestacion de publicaciones aprobadas en LinkedIn.

No ejecuta acciones al importarse. Cada publicacion requiere una llamada
explicita desde un endpoint autenticado y confirmacion previa en la interfaz.
"""

import re
from pathlib import Path
from typing import Literal

from fastapi import HTTPException

from app.content_workflow.service import solicitar_motor
from app.linkedin_oauth.image_upload import cargar_imagen_linkedin
from app.linkedin_oauth.profile import obtener_perfil_linkedin
from app.linkedin_oauth.publisher import (
    LinkedInPublishError,
    LinkedInResultUnknown,
    publicar_imagen_linkedin,
    publicar_texto_linkedin,
)
from app.linkedin_oauth.token_store import obtener_token

TipoContenido = Literal["texto", "texto_imagen", "imagen"]
PREFIJO_IMAGEN = "/api/v1/content-workflow/corporate-images/"


def _leer_imagen_corporativa(referencia: str) -> bytes:
    if not isinstance(referencia, str) or not referencia.startswith(PREFIJO_IMAGEN):
        raise ValueError("El contenido no tiene una referencia de imagen corporativa valida.")
    imagen_id = referencia[len(PREFIJO_IMAGEN):]
    if re.fullmatch(r"[a-f0-9]{32}", imagen_id) is None:
        raise ValueError("Identificador de imagen corporativa invalido.")

    # Reutiliza la misma ubicacion de imagenes que la publicacion Discord.
    from app.content_workflow.routes import _corporate_image_dir

    ruta = Path(_corporate_image_dir()) / f"{imagen_id}.png"
    if not ruta.is_file():
        raise ValueError("No se encontro la imagen corporativa aprobada.")
    imagen = ruta.read_bytes()
    if not imagen.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("La imagen corporativa no es un PNG valido.")
    if len(imagen) > 10 * 1024 * 1024:
        raise ValueError("La imagen corporativa supera el limite de 10 MB.")
    return imagen


def _marcar_desconocido(contenido_id: int, intento_id: str) -> None:
    solicitar_motor(
        "POST",
        f"/api/content/{contenido_id}/linkedin/unknown",
        datos={
            "intento_id": intento_id,
            "detalle": "El resultado de la publicacion debe verificarse manualmente.",
        },
    )


def publicar_contenido_linkedin(
    *, contenido_id: int, user_id: int, tipo_contenido: TipoContenido
) -> dict:
    if contenido_id <= 0 or user_id <= 0:
        raise HTTPException(status_code=422, detail="Identificador invalido.")
    if tipo_contenido not in ("texto", "texto_imagen", "imagen"):
        raise HTTPException(status_code=422, detail="Modalidad LinkedIn invalida.")

    token = obtener_token(user_id)
    if not token:
        raise HTTPException(status_code=409, detail="Conecta LinkedIn antes de publicar.")

    perfil = obtener_perfil_linkedin(user_id)
    author_urn = perfil.author_urn

    # La reserva devuelve el texto y la referencia de imagen aprobados.
    # Se libera el intento si falla una validacion antes de crear el post.
    reserva = solicitar_motor(
        "POST",
        f"/api/content/{contenido_id}/linkedin/reserve",
        datos={"author_urn": author_urn, "tipo_contenido": tipo_contenido},
    )
    intento_id = reserva["intento_id"]
    texto = reserva.get("contenido") or ""
    post_iniciado = False

    try:
        if tipo_contenido != "imagen" and not texto.strip():
            raise ValueError("El contenido aprobado no tiene texto para publicar.")
        imagen = (
            _leer_imagen_corporativa(reserva.get("imagen_generada_url"))
            if tipo_contenido != "texto" else None
        )

        if imagen is None:
            post_iniciado = True
            post_urn = publicar_texto_linkedin(
                access_token=token, author_urn=author_urn, texto=texto
            )
        else:
            image_urn = cargar_imagen_linkedin(
                access_token=token, author_urn=author_urn, imagen_png=imagen
            )
            post_iniciado = True
            post_urn = publicar_imagen_linkedin(
                access_token=token,
                author_urn=author_urn,
                image_urn=image_urn,
                texto=texto if tipo_contenido == "texto_imagen" else "",
            )
    except Exception as error:
        # Nunca se reintenta automaticamente. Si el POST pudo llegar a
        # LinkedIn, se conserva el intento para revision manual.
        if post_iniciado:
            _marcar_desconocido(contenido_id, intento_id)
            raise HTTPException(
                status_code=409,
                detail="Resultado LinkedIn no verificable; no reintentar.",
            ) from error

        solicitar_motor(
            "POST",
            f"/api/content/{contenido_id}/linkedin/release",
            datos={"intento_id": intento_id},
        )
        if isinstance(error, (ValueError, LinkedInPublishError)):
            raise HTTPException(status_code=409, detail=str(error)) from error
        raise

    # LinkedIn ya devolvio un identificador: no repetir el POST.
    try:
        confirmacion = solicitar_motor(
            "POST",
            f"/api/content/{contenido_id}/linkedin/confirm",
            datos={
                "intento_id": intento_id,
                "author_urn": author_urn,
                "tipo_contenido": tipo_contenido,
                "post_urn": post_urn,
            },
        )
    except Exception as error:
        try:
            _marcar_desconocido(contenido_id, intento_id)
        except Exception:
            pass
        raise HTTPException(
            status_code=409,
            detail=(
                "LinkedIn devolvio un identificador, pero CloudEdTech "
                "no pudo confirmar el registro. No reintentar."
            ),
        ) from error
    return {
        "status": "publicado",
        "contenido_id": contenido_id,
        "post_urn": post_urn,
        "confirmacion": confirmacion,
    }
