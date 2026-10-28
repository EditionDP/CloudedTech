"""Control de canales autorizados para el foro educativo.

Por defecto, ningun canal esta habilitado.
Este modulo no publica mensajes en Discord.
"""

import os
import re


PATRON_ID = re.compile(r"[0-9]{1,32}")


def normalizar_id(valor):
    if isinstance(valor, bool) or not isinstance(valor, (str, int)):
        raise ValueError("Identificador de Discord invalido")

    identificador = str(valor).strip()

    if not PATRON_ID.fullmatch(identificador):
        raise ValueError("Formato de identificador invalido")

    if int(identificador) <= 0:
        raise ValueError("Identificador debe ser positivo")

    return str(int(identificador))


def canales_educativos_autorizados():
    """Lee IDs separados por comas, sin habilitar ninguno por defecto."""

    configuracion = os.getenv(
        "CLOUDEDTECH_DISCORD_EDUCATIONAL_CHANNEL_IDS",
        "",
    ).strip()

    if not configuracion:
        return set()

    canales = set()

    for elemento in configuracion.split(","):
        elemento = elemento.strip()

        if not elemento:
            raise ValueError(
                "Configuracion de canales educativos invalida"
            )

        canales.add(normalizar_id(elemento))

    return canales


def canal_educativo_autorizado(channel_id):
    """Comprueba autorizacion; falla cerrado ante configuracion invalida."""

    try:
        canal = normalizar_id(channel_id)
        autorizados = canales_educativos_autorizados()
    except ValueError:
        return False

    return canal in autorizados
