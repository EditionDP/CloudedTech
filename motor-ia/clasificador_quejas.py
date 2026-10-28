"""Deteccion inicial de posibles quejas de la comunidad."""

import re
import unicodedata


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )
    return texto.casefold().strip()


PATRONES_QUEJA = (
    r"\bno (?:he|hemos|ha|han) logrado recibir respuestas?\b",
    r"\b(?:sigo|seguimos|estoy|estamos) esperando (?:una? )?respuestas?\b",
    r"\b(?:llevo|llevamos) .{0,60}esperando (?:una? )?respuestas?\b",
    r"\b(?:esperando|sin recibir) .{0,60}respuestas? .{0,40}(?:quejas?|reclamos?)\b",
    r"\b(?:mis|nuestras) (?:quejas?|reclamos?)\b",
    r"\b(?:no|nunca) (?:me|nos) (?:han )?respondido\b",

    r"\b(?:quiero|necesito|deseo)\s+(?:presentar|poner|registrar)\s+(?:una?\s+)?(?:queja|reclamo)\b",
    r"\b(?:tengo|presento)\s+(?:una?\s+)?(?:queja|reclamo)\b",
    r"\b(?:no puedo|no logro|no me deja)\s+(?:acceder|ingresar|entrar|descargar|inscribirme|registrarme)\b",
    r"\b(?:no funciona|no me funciona|no esta funcionando)\b",
    r"\b(?:no he recibido|no recibi|no me han enviado)\b",
    r"\b(?:llevo|hace)\s+(?:varios|muchos|dos|tres|cuatro|\d+)\s+dias?\b",
    r"\b(?:nadie me responde|no me responden|sin respuesta)\b",
    r"\b(?:problema|inconveniente|error)\s+(?:con|en|para)\b",
    r"\b(?:mala atencion|mal servicio|servicio deficiente)\b",
    r"\b(?:solicito una solucion|necesito una solucion)\b",
    # CLOUD_EDTECH_PASO_3211_DT
    '\\bno (?:dan|dieron|recibo|recibimos) respuestas?\\b',
    '\\b(?:muy|demasiado|bastante) lentas? las respuestas?\\b',
    '\\b(?:respuestas?|atencion) (?:muy )?lentas?\\b',
    '\\bno (?:dan|dieron) respuesta rapido\\b',
)


def clasificar_queja(texto, canal=None):
    """Devuelve una candidatura, nunca una queja confirmada."""
    normalizado = normalizar_texto(texto)

    coincidencias = [
        patron for patron in PATRONES_QUEJA
        if re.search(patron, normalizado)
    ]

    es_candidata = bool(coincidencias)

    return {
        "es_queja": es_candidata,
        "clasificacion": (
            "candidata" if es_candidata else "no_detectada"
        ),
        "estado_queja": (
            "pendiente" if es_candidata else "sin_clasificar"
        ),
        "canal_origen": canal,
        "metodo": "reglas_iniciales",
        "coincidencias": len(coincidencias),
        "requiere_revision": es_candidata,
    }
