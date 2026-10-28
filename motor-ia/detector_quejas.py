"""
Deteccion preliminar de quejas y solicitudes de soporte.

No publica mensajes ni realiza llamadas externas.
"""

import re
import unicodedata


PATRONES_QUEJA = (
    r"\bno (?:puedo|logro|me deja|funciona|carga|abre|responde)\b",
    r"\bno (?:he podido|me permite|tengo acceso)\b",
    r"\b(?:error|falla|fallo|inconformidad|inconforme|reclamo|queja)\b",
    r"\b(?:tengo|tenemos|presenta|presento|estoy teniendo|estamos teniendo) (?:un |varios )?problemas?\b",
    r"\bproblemas? (?:con|en|al|para acceder)\b",
    r"\b(?:se cae|esta caido|esta fallando|no sirve)\b",
    r"\b(?:necesito soporte|solicito ayuda|solicito solucion)\b",
    r"\b(?:me cobraron|cobro indebido|no recib[ií])\b",
    r"\b(?:mala atencion|pesimo servicio|sin respuesta)\b",
)


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )
    return re.sub(r"\s+", " ", texto.lower()).strip()


def detectar_queja(texto: str, canal: str = "") -> bool:
    texto_normalizado = normalizar(texto)
    canal_normalizado = normalizar(canal).lstrip("#")

    if not texto_normalizado:
        return False

    if canal_normalizado == "pqrs":
        return True

    return any(
        re.search(patron, texto_normalizado)
        for patron in PATRONES_QUEJA
    )
