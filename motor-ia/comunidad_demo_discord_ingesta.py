"""Integracion controlada de Discord con Ingesta."""

from datetime import datetime, timezone

from comunidad_demo_webhook_publicador import (
    publicar_webhook,
    preparar_mensaje_webhook,
)


def construir_actividad_discord(mensaje, publicacion):
    """Crea actividad con identificadores reales de Discord."""

    if publicacion.get("estado") != "publicado":
        raise ValueError("Publicacion no confirmada")

    preparado = preparar_mensaje_webhook(mensaje)

    guild_id = "1562138935948353588"
    channel_id = str(publicacion["channel_id"])
    message_id = str(publicacion["message_id"])

    return {
        "origen_comunidad": "Discord_Grupo_ONE_G10",
        "periodo_referencia": "Semana_01",
        "interacciones": [{
            "autor": preparado["nombre"],
            "canal": "#" + preparado["canal"],
            "texto": preparado["contenido"],
            "guild_id": guild_id,
            "guild_name": "CloudEDTech_OF",
            "channel_id": channel_id,
            "message_id": message_id,
            "author_id": "webhook_simulacion_cloudedtech",
            "attachments": [],
            "enviado_en": datetime.now(timezone.utc).isoformat(),
        }],
    }


def publicar_y_registrar(mensaje, *, confirmar=False):
    """Publica una vez y registra solamente tras confirmacion."""

    if confirmar is not True:
        return publicar_webhook(mensaje, confirmar=False)

    resultado = publicar_webhook(mensaje, confirmar=True)

    if resultado.get("estado") != "publicado":
        return resultado

    if mensaje.get("canal") == "foro-educativo":
        hilo_esperado = "1563254807479976018"
        hilo_configurado = str(resultado.get("thread_id"))
        canal_confirmado = str(resultado.get("channel_id"))

        if (
            hilo_configurado != hilo_esperado
            or canal_confirmado != hilo_esperado
        ):
            return {
                "publicacion": resultado,
                "ingesta": None,
                "destino": "foro-educativo",
                "motivo": "destino_educativo_no_verificado",
            }

        return {
            "publicacion": resultado,
            "ingesta": None,
            "destino": "foro-educativo",
            "motivo": "foro_educativo_excluido_de_ingesta",
        }

    actividad = construir_actividad_discord(mensaje, resultado)

    from procesamiento import procesar_actividad

    procesamiento = procesar_actividad(actividad)

    return {
        "publicacion": resultado,
        "ingesta": procesamiento,
    }
