"""
Respuestas educativas simuladas entre participantes.

No envia mensajes, no consulta servicios externos
y no escribe en bases de datos.
"""

import random
import uuid

from comunidad_demo_usuarios import obtener_participantes
from respuestas_foro_tecnologico import preparar_respuesta


def generar_respuesta_simulada(pregunta, rng=None):
    if not isinstance(pregunta, dict):
        raise ValueError("La pregunta debe ser un diccionario")

    if (
        pregunta.get("origen") != "discord_demo"
        or pregunta.get("es_simulado") is not True
        or pregunta.get("publicar_discord") is not False
    ):
        raise ValueError("Solo se permiten preguntas simuladas")

    identificador = pregunta.get("id_simulacion")
    autor_original = pregunta.get("autor")
    texto = pregunta.get("texto")

    if not all(
        isinstance(valor, str) and valor.strip()
        for valor in (identificador, autor_original, texto)
    ):
        raise ValueError("Datos de pregunta incompletos")

    participantes = obtener_participantes()

    if autor_original not in participantes:
        raise ValueError("Autor original no reconocido")

    resultado = preparar_respuesta(texto)

    if resultado.get("estado") != "borrador":
        return {
            "estado": "sin_respuesta_automatica",
            "motivo": resultado.get("motivo"),
            "id_pregunta": identificador,
            "respuesta": None,
            "publicar_discord": False,
        }

    respuesta = resultado.get("respuesta")

    if not isinstance(respuesta, str) or not respuesta.strip():
        raise ValueError("Borrador educativo vacio")

    candidatos = [
        participante
        for participante in participantes
        if participante != autor_original
    ]

    if not candidatos:
        raise ValueError("No hay participantes disponibles")

    rng = rng or random.SystemRandom()
    autor_respuesta = rng.choice(candidatos)

    return {
        "estado": "respuesta_simulada",
        "id_simulacion": f"demo_reply_{uuid.uuid4().hex}",
        "id_pregunta": identificador,
        "autor": autor_respuesta,
        "autor_pregunta": autor_original,
        "canal": pregunta.get("canal", "preguntas"),
        "tema": pregunta.get("tema"),
        "texto": respuesta,
        "origen": "discord_demo",
        "es_simulado": True,
        "publicar_discord": False,
        "es_respuesta_oficial": False,
    }
