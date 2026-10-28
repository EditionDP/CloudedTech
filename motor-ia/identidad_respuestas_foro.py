"""
Identidad determinista de mensajes originales de Discord.

Este modulo no guarda datos, no publica mensajes y no consulta redes.
"""

import hashlib
import re


PATRON_ID = re.compile(r"[0-9]{1,32}$")


def validar_id_discord(valor: object, campo: str) -> str:
    if isinstance(valor, bool):
        raise ValueError(f"{campo}: identificador invalido")

    if not isinstance(valor, (str, int)):
        raise ValueError(f"{campo}: tipo de identificador invalido")

    identificador = str(valor).strip()

    if not PATRON_ID.fullmatch(identificador):
        raise ValueError(f"{campo}: formato de identificador invalido")

    if int(identificador) <= 0:
        raise ValueError(f"{campo}: identificador debe ser positivo")

    return str(int(identificador))


def identidad_mensaje_discord(
    guild_id: object,
    channel_id: object,
    message_id: object,
) -> dict:
    servidor = validar_id_discord(guild_id, "guild_id")
    canal = validar_id_discord(channel_id, "channel_id")
    mensaje = validar_id_discord(message_id, "message_id")

    referencia = f"discord:{servidor}:{canal}:{mensaje}"

    return {
        "guild_id": servidor,
        "channel_id": canal,
        "source_message_id": mensaje,
        "clave_unica": hashlib.sha256(
            referencia.encode("utf-8")
        ).hexdigest(),
    }
