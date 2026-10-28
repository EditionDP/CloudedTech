"""Generacion local de reacciones sinteticas.

Los conteos son absolutos y compatibles con discord_reacciones.
No se conecta a Discord ni escribe en bases de datos.
"""

import random

EMOJIS_PERMITIDOS = (
    "\U0001F44D",
    "\u2764\ufe0f",
    "\U0001F525",
    "\U0001F602",
    "\U0001F389",
    "\U0001F680",
)


def generar_reacciones(rng=None, maximo=12):
    """Genera un estado inicial de reacciones."""
    if type(maximo) is not int or not 1 <= maximo <= 100:
        raise ValueError("Maximo de reacciones invalido")

    rng = rng or random.SystemRandom()
    cantidad_emojis = rng.randint(1, len(EMOJIS_PERMITIDOS))
    emojis = rng.sample(EMOJIS_PERMITIDOS, cantidad_emojis)

    return [
        {
            "emoji": emoji,
            "cantidad": rng.randint(1, maximo),
        }
        for emoji in emojis
    ]


def evolucionar_reacciones(reacciones, rng=None, incremento_maximo=4):
    """Devuelve nuevos conteos sin modificar los anteriores."""
    if not isinstance(reacciones, list):
        raise ValueError("Las reacciones deben ser una lista")

    if type(incremento_maximo) is not int or not 1 <= incremento_maximo <= 100:
        raise ValueError("Incremento invalido")

    vistos = set()
    anteriores = {}

    for reaccion in reacciones:
        if not isinstance(reaccion, dict):
            raise ValueError("Reaccion invalida")

        emoji = reaccion.get("emoji")
        cantidad = reaccion.get("cantidad")

        if emoji not in EMOJIS_PERMITIDOS or emoji in vistos:
            raise ValueError("Emoji invalido o duplicado")

        if type(cantidad) is not int or cantidad < 0:
            raise ValueError("Cantidad invalida")

        vistos.add(emoji)
        anteriores[emoji] = cantidad

    rng = rng or random.SystemRandom()

    if not vistos:
        emoji = rng.choice(EMOJIS_PERMITIDOS)
    else:
        disponibles = [
            emoji for emoji in EMOJIS_PERMITIDOS
            if emoji not in vistos
        ]
        opciones = list(vistos) + disponibles

        emoji = rng.choice(opciones)

    anteriores[emoji] = (
        anteriores.get(emoji, 0)
        + rng.randint(1, incremento_maximo)
    )

    return [
        {"emoji": emoji, "cantidad": cantidad}
        for emoji, cantidad in anteriores.items()
        if cantidad > 0
    ]
