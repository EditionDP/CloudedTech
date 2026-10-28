"""
Identificadores exclusivos para la comunidad simulada.

No genera identificadores reales de Discord.
No escribe bases de datos ni publica mensajes.
"""

import uuid

from comunidad_demo_usuarios import obtener_participantes


GUILD_ID_DEMO = "cloudedtech_demo_guild"

CANALES_DEMO = {
    "general": "cloudedtech_demo_general",
    "preguntas": "cloudedtech_demo_preguntas",
    "chat-egresados": "cloudedtech_demo_egresados",
    "oportunidades-laborales": "cloudedtech_demo_oportunidades",
    "faq": "cloudedtech_demo_faq",
    "pqrs": "cloudedtech_demo_pqrs",
    "notificaciones": "cloudedtech_demo_notificaciones",
    "foro-educativo": "cloudedtech_demo_foro_educativo",
}


def generar_identidad_mensaje(mensaje):
    if not isinstance(mensaje, dict):
        raise ValueError("Mensaje invalido")

    if (
        mensaje.get("origen") != "discord_demo"
        or mensaje.get("es_simulado") is not True
        or mensaje.get("publicar_discord") is not False
    ):
        raise ValueError("Solo se admiten mensajes simulados")

    autor = mensaje.get("autor")
    canal = mensaje.get("canal")
    identificador = mensaje.get("id_simulacion")

    if autor not in obtener_participantes():
        raise ValueError("Participante no reconocido")

    if canal not in CANALES_DEMO:
        raise ValueError("Canal no reconocido")

    if (
        not isinstance(identificador, str)
        or not identificador.startswith("demo_")
        or not identificador.strip()
    ):
        raise ValueError("Identificador de simulacion invalido")

    return {
        "guild_id": GUILD_ID_DEMO,
        "guild_name": "CloudEdTech Comunidad Simulada",
        "channel_id": CANALES_DEMO[canal],
        "message_id": identificador,
        "author_id": (
            "cloudedtech_demo_user_"
            + str(obtener_participantes().index(autor) + 1).zfill(3)
        ),
        "id_pregunta": mensaje.get("id_pregunta"),
        "origen_comunidad": "discord_demo",
        "es_simulado": True,
        "publicar_discord": False,
    }
