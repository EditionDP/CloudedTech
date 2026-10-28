"""Integracion segura del generador y el historial demo.

La conexion SQLite es proporcionada por el llamador.
No publica en Discord ni inicia tareas automaticas.
"""

from comunidad_demo_conversaciones import (
    TEMAS,
    CONTEXTOS,
    PREGUNTAS,
    generar_consulta,
)
from comunidad_demo_historial import (
    cargar_preguntas_utilizadas,
    normalizar_pregunta,
    registrar_pregunta,
)


def generar_y_registrar(conexion, tema, rng=None):
    """Genera y registra una pregunta sin repetir el historial."""
    from comunidad_demo_conversaciones import (
        MENSAJES_POR_CANAL,
        DESTINOS,
        consultar_configuracion,
    )

    if tema not in (*TEMAS, "mixto"):
        raise ValueError("Tema no autorizado")

    utilizados = cargar_preguntas_utilizadas(conexion)

    config = consultar_configuracion()
    canales = [
        canal for canal in config["canales"]
        if canal in DESTINOS and canal in MENSAJES_POR_CANAL
    ]

    disponibles = {
        normalizar_pregunta(texto)
        for canal in canales
        for texto in MENSAJES_POR_CANAL[canal]
    }

    restantes = disponibles - utilizados

    if not restantes:
        raise ValueError(
            "No quedan conversaciones nuevas en los canales habilitados"
        )

    usados_generador = {
        texto.casefold()
        for canal in canales
        for texto in MENSAJES_POR_CANAL[canal]
        if normalizar_pregunta(texto) in utilizados
    }

    mensaje = generar_consulta(
        tema,
        usados=usados_generador,
        rng=rng,
    )

    if not registrar_pregunta(conexion, mensaje):
        raise RuntimeError("La pregunta ya estaba registrada")

    return mensaje
