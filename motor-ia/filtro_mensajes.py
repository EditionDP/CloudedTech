"""
Clasificacion conservadora de mensajes triviales de Discord.

No elimina mensajes ni realiza operaciones de red.
Solo identifica expresiones breves sin contenido sustantivo.
"""

import re
import unicodedata


EXPRESIONES_TRIVIALES = frozenset({
    "hola",
    "holaa",
    "holaaa",
    "buenas",
    "buenas tardes",
    "buenos dias",
    "buenas noches",
    "que tal",
    "qu tal",
    "como estan",
    "como estas",
    "saludos",
    "hey",
    "hello",
    "hi",
    "ok",
    "okay",
    "oki",
    "vale",
    "listo",
    "dale",
    "de acuerdo",
    "entendido",
    "perfecto",
    "gracias",
    "muchas gracias",
    "mil gracias",
    "ok gracias",
    "vale gracias",
    "listo gracias",
    "hola gracias",
    "jaja",
    "jajaja",
    "jeje",
    "jejeje",
    "xd",
    "si",
    "no",
})


def normalizar_para_filtro(texto: str) -> str:
    """Normaliza acentos, mayusculas y puntuacion superficial."""
    if not isinstance(texto, str):
        return ""

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    texto = texto.casefold()
    texto = re.sub(r"[^a-z0-9\\s]", " ", texto)
    return " ".join(texto.split())


def es_mensaje_trivial(texto: str) -> bool:
    """Devuelve True solo para expresiones triviales conocidas."""
    normalizado = normalizar_para_filtro(texto)

    if not normalizado:
        return True

    return normalizado in EXPRESIONES_TRIVIALES
