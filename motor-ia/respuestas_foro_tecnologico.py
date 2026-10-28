"""
Preparacion local de respuestas educativas para el foro tecnologico.

No envia mensajes, no consulta APIs externas y no modifica datos.
Las respuestas son propuestas, no publicaciones.
"""

from clasificador_foro_tecnologico import (
    clasificar_consulta,
    normalizar,
)


EXPLICACIONES = {
    "api": (
        "Una API es una interfaz que permite que dos aplicaciones "
        "intercambien informacion mediante reglas definidas. "
        "Por ejemplo, una pagina web puede consultar una API "
        "para mostrar datos de un servidor."
    ),
    "python": (
        "Python es un lenguaje de programacion utilizado en "
        "automatizacion, desarrollo web, analisis de datos e "
        "inteligencia artificial. Para comenzar, puedes aprender "
        "variables, condicionales, ciclos y funciones."
    ),
    "sql": (
        "SQL es un lenguaje para consultar y administrar datos "
        "en bases de datos relacionales. NoSQL agrupa distintos "
        "modelos de almacenamiento, como documentos o clave-valor. "
        "La eleccion depende de las relaciones y consultas necesarias."
    ),
    "inteligencia artificial": (
        "La inteligencia artificial permite desarrollar sistemas "
        "que realizan tareas como reconocer patrones, clasificar "
        "informacion y generar contenido. Para aprender, conviene "
        "comenzar por Python, datos y fundamentos de aprendizaje "
        "automatico."
    ),
    "docker": (
        "Docker permite empaquetar aplicaciones y sus dependencias "
        "en contenedores. Esto facilita ejecutar el mismo software "
        "de manera consistente en diferentes entornos."
    ),
    "postgresql": (
        "PostgreSQL es un sistema de gestion de bases de datos "
        "relacionales. Para comenzar, puedes practicar la creacion "
        "de tablas, consultas SQL, claves y relaciones."
    ),
    "ciberseguridad": (
        "La ciberseguridad busca proteger sistemas, redes y datos. "
        "Entre sus fundamentos estan la autenticacion, el control "
        "de acceso, las actualizaciones y la proteccion de credenciales."
    ),
    "react": (
        "React es una biblioteca de JavaScript para construir "
        "interfaces mediante componentes. Para aprenderla, "
        "conviene dominar componentes, propiedades, estado y eventos."
    ),
}

ORDEN_TEMAS = (
    "postgresql",
    "inteligencia artificial",
    "ciberseguridad",
    "docker",
    "python",
    "react",
    "api",
    "sql",
)


def requiere_respuesta_contextual(texto: str) -> bool:
    """Detecta consultas que necesitan contexto, diagnostico o instrucciones."""
    normalizado = normalizar(texto)

    indicadores = (
        "tengo un error",
        "tengo errores",
        "me aparece un error",
        "me sale un error",
        "no funciona",
        "no puedo",
        "tengo un problema",
        "tengo problemas",
        "como configurar",
        "como instalar",
        "como implementar",
        "como solucionar",
        "como resolver",
        "necesito ayuda",
        "me falla",
        "se bloquea",
        "no conecta",
        "no compila",
    )

    return any(
        indicador in normalizado
        for indicador in indicadores
    )


def preparar_respuesta(texto: str) -> dict:
    clasificacion = clasificar_consulta(texto)

    if not clasificacion["es_consulta_tecnologica"]:
        return {
            "estado": "no_aplica",
            "motivo": clasificacion["motivo"],
            "respuesta": None,
            "publicar": False,
        }

    temas = clasificacion["temas"]
    normalizado = normalizar(texto)

    if requiere_respuesta_contextual(texto):
        return {
            "estado": "requiere_revision",
            "motivo": "consulta_requiere_contexto",
            "temas": temas,
            "respuesta": None,
            "publicar": False,
        }

    for tema in ORDEN_TEMAS:
        if tema not in temas:
            continue

        # Evitar explicar SQL generico cuando la consulta
        # menciona NoSQL y no existe una respuesta adecuada.
        if tema == "sql" and "nosql" in temas:
            pass

        respuesta = EXPLICACIONES[tema]

        return {
            "estado": "borrador",
            "motivo": "respuesta_educativa_local",
            "tema": tema,
            "pregunta_original": texto,
            "respuesta": respuesta,
            "publicar": False,
        }

    return {
        "estado": "requiere_revision",
        "motivo": "sin_respuesta_local_para_el_tema",
        "temas": temas,
        "respuesta": None,
        "publicar": False,
    }
