"""
Adaptador de mensajes simulados al esquema de ingesta.

No escribe bases de datos ni publica en Discord.
"""

from datetime import datetime, timezone

from comunidad_demo_identidades import generar_identidad_mensaje
from modelos import SolicitudActividad


def construir_actividad_simulada(mensaje):
    identidad = generar_identidad_mensaje(mensaje)

    texto = mensaje.get("texto")

    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Texto simulado invalido")

    if mensaje.get("publicar_discord") is not False:
        raise ValueError("Publicacion no autorizada")

    paquete = {
        "origen_comunidad": "discord_demo",
        "periodo_referencia": datetime.now(
            timezone.utc
        ).strftime("%Y-W%W"),
        "interacciones": [
            {
                "autor": mensaje["autor"],
                "canal": mensaje["canal"],
                "texto": texto,
                "tipo": "mensaje",
                "enviado_en": datetime.now(
                    timezone.utc
                ).isoformat(),
                "guild_id": identidad["guild_id"],
                "guild_name": identidad["guild_name"],
                "channel_id": identidad["channel_id"],
                "message_id": identidad["message_id"],
                "author_id": identidad["author_id"],
                "attachments": [],
            }
        ],
    }

    validado = SolicitudActividad.model_validate(paquete)

    return {
        "actividad": validado.model_dump(mode="json"),
        "origen_comunidad": "discord_demo",
        "es_simulado": True,
        "publicar_discord": False,
        "id_simulacion": mensaje["id_simulacion"],
        "id_pregunta": mensaje.get("id_pregunta"),
    }
