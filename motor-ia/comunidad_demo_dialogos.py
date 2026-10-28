"""
Variaciones conversacionales para respuestas simuladas.

No altera explicaciones tecnicas originales.
No escribe bases de datos ni publica mensajes.
"""

import random

from comunidad_demo_respuestas import generar_respuesta_simulada


INTRODUCCIONES = (
    "Te comparto una explicacion que puede ayudarte:",
    "Yo empezaria por entender lo siguiente:",
    "Una forma sencilla de verlo es esta:",
    "Esto fue lo primero que aprendi sobre el tema:",
    "Para comenzar, revisaria estos fundamentos:",
    "Te dejo una explicacion introductoria:",
    "Una buena base para estudiar el tema es esta:",
    "Creo que esta explicacion puede orientarte:",
)

CIERRES = (
    "Espero que te sirva como punto de partida.",
    "Puedes continuar practicando con ejemplos sencillos.",
    "Si tienes dudas concretas, podemos revisarlas.",
    "Lo importante es comprender primero los fundamentos.",
    "Despues puedes profundizar con ejercicios practicos.",
    "Es un buen tema para seguir investigando.",
    "Puedes tomarlo como una introduccion al tema.",
    "Conviene complementar esto con documentacion oficial.",
)


def generar_dialogo(pregunta, rng=None):
    rng = rng or random.SystemRandom()

    respuesta = generar_respuesta_simulada(
        pregunta,
        rng=rng,
    )

    if respuesta["estado"] != "respuesta_simulada":
        return respuesta

    explicacion = respuesta["texto"]

    introduccion = rng.choice(INTRODUCCIONES)
    cierre = rng.choice(CIERRES)

    respuesta = dict(respuesta)

    respuesta["texto"] = (
        introduccion
        + "\n\n"
        + explicacion
        + "\n\n"
        + cierre
    )

    respuesta["explicacion_original"] = explicacion
    respuesta["tipo_intervencion"] = "respuesta_educativa"

    return respuesta
