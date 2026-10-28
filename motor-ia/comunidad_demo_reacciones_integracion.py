"""
Vincula reacciones simuladas con mensajes simulados.

No modifica bases de datos ni publica en Discord.
"""

from comunidad_demo_identidades import (
    generar_identidad_mensaje,
)
from comunidad_demo_reacciones import (
    generar_reacciones,
    evolucionar_reacciones,
)


def crear_estado_reacciones(mensaje, rng=None):
    identidad = generar_identidad_mensaje(mensaje)

    reacciones = generar_reacciones(rng=rng)

    return {
        "guild_id": identidad["guild_id"],
        "channel_id": identidad["channel_id"],
        "message_id": identidad["message_id"],
        "origen_comunidad": "discord_demo",
        "es_simulado": True,
        "publicar_discord": False,
        "reacciones": reacciones,
    }


def incrementar_estado_reacciones(estado, rng=None):
    if not isinstance(estado, dict):
        raise ValueError("Estado invalido")

    if (
        estado.get("origen_comunidad") != "discord_demo"
        or estado.get("es_simulado") is not True
        or estado.get("publicar_discord") is not False
    ):
        raise ValueError("Origen de reacciones no autorizado")

    if estado.get("guild_id") != "cloudedtech_demo_guild":
        raise ValueError("Servidor simulado invalido")

    if not isinstance(estado.get("channel_id"), str):
        raise ValueError("Canal invalido")

    if not estado["channel_id"].startswith("cloudedtech_demo_"):
        raise ValueError("Canal no simulado")

    if not isinstance(estado.get("message_id"), str):
        raise ValueError("Mensaje invalido")

    if not estado["message_id"].startswith("demo_"):
        raise ValueError("Mensaje no simulado")

    anteriores = estado.get("reacciones")

    nuevas = evolucionar_reacciones(
        anteriores,
        rng=rng,
    )

    actualizado = dict(estado)
    actualizado["reacciones"] = nuevas

    return actualizado
