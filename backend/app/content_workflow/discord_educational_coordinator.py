"""Coordinacion de borradores educativos sin publicacion en Discord."""

from app.content_workflow.discord_educational_response_service import (
    registrar_borrador_educativo,
)


def coordinar_borrador_educativo(
    db,
    *,
    guild_id,
    channel_id,
    message_id,
    texto,
    preparar,
    crear_identidad,
    canal_autorizado,
):
    """Clasifica una consulta y guarda solo borradores educativos."""

    if not isinstance(texto, str):
        raise ValueError("El mensaje debe ser texto")

    if not texto.strip():
        return {
            "estado": "no_aplica",
            "motivo": "texto_vacio",
            "publicar": False,
        }

    if not callable(canal_autorizado):
        raise ValueError("Validador de canal no disponible")

    if canal_autorizado(channel_id) is not True:
        return {
            "estado": "no_aplica",
            "motivo": "canal_no_autorizado",
            "publicar": False,
        }

    resultado = preparar(texto)

    if not isinstance(resultado, dict):
        raise ValueError("Resultado educativo invalido")

    estado = resultado.get("estado")

    if estado in {"no_aplica", "requiere_revision"}:
        return {
            "estado": estado,
            "motivo": resultado.get("motivo"),
            "publicar": False,
        }

    if estado != "borrador":
        raise ValueError("Estado educativo desconocido")

    if resultado.get("publicar") is not False:
        raise ValueError("La preparacion no debe autorizar publicacion")

    respuesta = resultado.get("respuesta")

    if not isinstance(respuesta, str) or not respuesta.strip():
        raise ValueError("Borrador educativo sin respuesta")

    identidad = crear_identidad(
        guild_id,
        channel_id,
        message_id,
    )

    registro, creado = registrar_borrador_educativo(
        db,
        identidad=identidad,
        pregunta_original=texto,
        respuesta=respuesta,
        tema=resultado.get("tema"),
    )

    return {
        "estado": "borrador",
        "creado": creado,
        "registro_id": registro.id,
        "tema": registro.tema,
        "publicar": False,
    }
