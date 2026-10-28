"""Generador local de consultas educativas para CloudEdTech.

No escribe bases de datos ni publica en Discord.
"""

import random
import uuid

from comunidad_demo_participantes import participantes_activos
from comunidad_demo_publicacion_config import consultar_configuracion, DESTINOS


TEMAS = {
    'ia': (
        'agentes de IA',
        'modelo de lenguaje',
        'inteligencia artificial',
        'chatbot',
        'machine learning',
    ),
    'programacion': (
        'Python',
        'React',
        'JavaScript',
        'FastAPI',
        'TypeScript',
    ),
    'ciberseguridad': (
        'autenticacion',
        'seguridad informatica',
        'ciberseguridad',
        'autorizacion',
        'seguridad de APIs REST',
    ),
    'datos': (
        'PostgreSQL',
        'consultas SQL',
        'APIs REST',
        'Docker',
        'computacion en la nube',
    ),
}

CONTEXTOS = (
    'en un proyecto universitario',
    'para una aplicación educativa',
    'en un proyecto de práctica',
    'si estoy comenzando a estudiar tecnología',
    'en una plataforma comunitaria',
    'durante un curso de programación',
)

PREGUNTAS = (
    '¿Qué es {tema} y para qué sirve {contexto}?',
    '¿Cómo funciona {tema} {contexto}?',
    '¿Cómo aprender {tema} con ejemplos prácticos {contexto}?',
    '¿Cómo implementar {tema} correctamente {contexto}?',
    '¿Cómo usar {tema} de forma segura {contexto}?',
    '¿Puedes explicar los fundamentos de {tema} {contexto}?',
)



# PASO 3211-BI: CONVERSACIONES CONTEXTUALIZADAS POR CANAL
MENSAJES_POR_CANAL = {'general': ('¿Qué tecnologías están aprendiendo actualmente en la comunidad?',
             '¿Qué proyectos de programación están desarrollando este mes?',
             '¿Alguien recomienda recursos gratuitos para aprender inteligencia artificial?',
             'Me gustaría participar en un proyecto colaborativo de tecnología. ¿Hay alguno '
             'activo?',
             'He tenido dificultades para encontrar información sobre las actividades de la '
             'comunidad. ¿Dónde puedo consultarlas?'),
 'faq': ('¿Cómo puedo comenzar a aprender Python si no tengo experiencia?',
         '¿Dónde encuentro las preguntas frecuentes sobre los cursos disponibles?',
         '¿Qué necesito instalar para comenzar a desarrollar aplicaciones con React?',
         '¿Cuál es la diferencia entre frontend y backend?',
         '¿Cómo puedo recuperar el acceso a mi cuenta si olvidé la contraseña?'),
 'pqrs': ('Quiero presentar una queja porque no recibí respuesta a mi solicitud de soporte.',
          '¿Dónde puedo consultar el estado de una petición enviada anteriormente?',
          'Tengo un reclamo: el enlace de inscripción al curso no funciona.',
          'Sugiero mejorar la información sobre los horarios de las actividades.',
          'La plataforma presenté errores y perdí el formulario que estaba completando.'),
 'chat-egresados': ('¿Cómo fue su experiencia buscando el primer empleo después de graduarse?',
                    '¿Qué conocimientos les han resultado más útiles en su vida profesional?',
                    '¿Alguien quiere compartir su experiencia trabajando como desarrollador?',
                    '¿Qué certificaciones recomendarían a los nuevos egresados?',
                    'Quiero reportar que el enlace de la bolsa de egresados no funciona. ¿Quién '
                    'puede ayudarme?'),
 'oportunidades-laborales': ('¿Conocen vacantes junior para desarrolladores Python o React?',
                             '¿Qué recomendaciones tienen para preparar una entrevista técnica?',
                             '¿Cómo puedo mejorar mi hoja de vida para postularme a empleos de '
                             'tecnología?',
                             '¿Dónde puedo encontrar oportunidades de trabajo remoto para '
                             'programadores?',
                             'Quiero reportar que una oferta laboral publicada tiene un enlace que '
                             'no funciona.'),
 'notificaciones': ('¿Cuándo se anunciarán las próximas actividades de la comunidad?',
                    '¿Dónde puedo consultar los avisos sobre nuevos cursos y talleres?',
                    '¿Existe alguna forma de recibir notificaciones de eventos educativos?',
                    'No recibí la notificación de una actividad importante. ¿Cómo puedo '
                    'reportarlo?',
                    '¿Se publicará un calendario actualizado de las próximas capacitaciones?'),
 'foro-educativo': ('¿Cómo funciona una API REST y cuándo conviene utilizarla?',
                    '¿Qué diferencias existen entre Python y JavaScript?',
                    '¿Cómo funciona la autenticación JWT en una aplicación web?',
                    '¿Qué es Docker y para qué sirve en un proyecto de software?',
                    '¿Cómo se relacionan las bases de datos PostgreSQL con una API FastAPI?')}


# PASO 3211-BY: AMPLIACION DINAMICA DEL FORO EDUCATIVO
def construir_preguntas_foro():
    preguntas = list(MENSAJES_POR_CANAL["foro-educativo"])
    vistos = {pregunta.casefold() for pregunta in preguntas}

    for asuntos in TEMAS.values():
        for asunto in asuntos:
            for contexto in CONTEXTOS:
                for plantilla in PREGUNTAS:
                    pregunta = plantilla.format(
                        tema=asunto,
                        contexto=contexto,
                    )

                    if pregunta.casefold() not in vistos:
                        preguntas.append(pregunta)
                        vistos.add(pregunta.casefold())

    return tuple(preguntas)


MENSAJES_POR_CANAL["foro-educativo"] = construir_preguntas_foro()


# PASO 3211-CB: CONVERSACIONES DINAMICAS POR CANAL
ASUNTOS_COMUNITARIOS = {
    "general": (
        "los proyectos colaborativos",
        "las herramientas de inteligencia artificial",
        "los grupos de estudio",
        "las actividades de la comunidad",
        "el aprendizaje de programacion",
        "los recursos educativos gratuitos",
        "la participacion en eventos tecnologicos",
        "las experiencias de aprendizaje",
    ),
    "faq": (
        "la inscripcion a los cursos",
        "el acceso a los materiales educativos",
        "la recuperacion de contrasenas",
        "los requisitos para participar en talleres",
        "el uso de la plataforma",
        "las certificaciones disponibles",
        "los horarios de las capacitaciones",
        "las herramientas necesarias para estudiar",
    ),
    "pqrs": (
        "la falta de respuesta del soporte",
        "los errores de acceso a la plataforma",
        "los enlaces de inscripcion que no funcionan",
        "los retrasos en las respuestas",
        "la informacion desactualizada",
        "los problemas para descargar certificados",
        "las dificultades para contactar administradores",
        "los inconvenientes con las notificaciones",
    ),
    "chat-egresados": (
        "la busqueda del primer empleo",
        "las entrevistas tecnicas",
        "las certificaciones profesionales",
        "la experiencia laboral en tecnologia",
        "el trabajo remoto",
        "los proyectos de portafolio",
        "la preparacion para entrevistas",
        "las oportunidades de crecimiento profesional",
    ),
    "oportunidades-laborales": (
        "las vacantes para desarrolladores junior",
        "las oportunidades de trabajo remoto",
        "las entrevistas de programacion",
        "la preparacion de hojas de vida",
        "las practicas profesionales",
        "las ofertas para analistas de datos",
        "las vacantes de ciberseguridad",
        "las oportunidades laborales en inteligencia artificial",
    ),
    "notificaciones": (
        "los proximos talleres",
        "los anuncios de nuevos cursos",
        "las fechas de inscripcion",
        "las actividades comunitarias",
        "las actualizaciones de la plataforma",
        "los recordatorios de eventos",
        "las novedades educativas",
        "los cambios en los horarios",
    ),
}

PLANTILLAS_COMUNITARIAS = {
    "general": (
        "\u00bfQu\u00bf opinan sobre {asunto}\u00bf",
        "\u00bfAlguien quiere compartir experiencias relacionadas con {asunto}\u00bf",
        "\u00bfQu\u00bf recomendaciones tienen sobre {asunto}\u00bf",
        "Me gustar\u00bfa conocer m\u00bfs sobre {asunto}. \u00bfPor d\u00bfnde puedo comenzar\u00bf",
    ),
    "faq": (
        "\u00bfD\u00bfnde puedo encontrar informaci\u00bfn sobre {asunto}\u00bf",
        "\u00bfCu\u00bfles son los pasos para gestionar {asunto}\u00bf",
        "\u00bfExiste alguna gu\u00bfa sobre {asunto}\u00bf",
        "\u00bfCon qui\u00bfn puedo resolver dudas relacionadas con {asunto}\u00bf",
    ),
    "pqrs": (
        "Quiero presentar una queja relacionada con {asunto}. \u00bfQui\u00bfn puede ayudarme\u00bf",
        "Tengo un reclamo sobre {asunto} y necesito una soluci\u00bfn.",
        "Solicito informaci\u00bfn sobre {asunto} porque no he recibido una respuesta clara.",
        "Sugiero mejorar la atenci\u00bfn relacionada con {asunto}.",
    ),
    "chat-egresados": (
        "\u00bfQu\u00bf experiencias tienen con {asunto}\u00bf",
        "\u00bfQu\u00bf consejos dar\u00bfan a otros egresados sobre {asunto}\u00bf",
        "Me gustar\u00bfa conocer experiencias reales sobre {asunto}.",
        "\u00bfAlguien puede compartir recomendaciones sobre {asunto}\u00bf",
    ),
    "oportunidades-laborales": (
        "\u00bfD\u00bfnde puedo encontrar informaci\u00bfn sobre {asunto}\u00bf",
        "\u00bfQu\u00bf requisitos suelen solicitar para {asunto}\u00bf",
        "\u00bfQu\u00bf recomendaciones tienen para prepararse para {asunto}\u00bf",
        "\u00bfAlguien conoce recursos o contactos relacionados con {asunto}\u00bf",
    ),
    "notificaciones": (
        "\u00bfD\u00bfnde puedo consultar informaci\u00bfn actualizada sobre {asunto}\u00bf",
        "\u00bfC\u00bfmo puedo recibir avisos relacionados con {asunto}\u00bf",
        "\u00bfSe publicar\u00bf un anuncio sobre {asunto}\u00bf",
        "No recib\u00bf informaci\u00bfn sobre {asunto}. \u00bfD\u00bfnde puedo reportarlo\u00bf",
    ),
}


def ampliar_conversaciones_comunitarias():
    for canal, asuntos in ASUNTOS_COMUNITARIOS.items():
        existentes = list(MENSAJES_POR_CANAL[canal])
        vistos = {texto.casefold() for texto in existentes}

        for asunto in asuntos:
            for plantilla in PLANTILLAS_COMUNITARIAS[canal]:
                texto = plantilla.format(asunto=asunto)

                if texto.casefold() not in vistos:
                    existentes.append(texto)
                    vistos.add(texto.casefold())

        MENSAJES_POR_CANAL[canal] = tuple(existentes)


ampliar_conversaciones_comunitarias()


# PASO 3202: ENRUTAMIENTO TEMATICO
CANALES_POR_CONTEXTO = {
    CONTEXTOS[0]: ("foro-educativo", "faq", "general"),
    CONTEXTOS[1]: ("foro-educativo", "faq", "general"),
    CONTEXTOS[2]: ("chat-egresados", "general"),
    CONTEXTOS[3]: ("faq", "foro-educativo", "general"),
    CONTEXTOS[4]: ("general", "foro-educativo"),
    CONTEXTOS[5]: ("foro-educativo", "faq", "general"),
}


def seleccionar_destino_discord(contexto, rng):
    config = consultar_configuracion()
    permitidos = config["canales"]

    if not permitidos:
        raise ValueError("No hay destinos Discord seleccionados.")

    candidatos = CANALES_POR_CONTEXTO.get(
        contexto,
        ("general", "foro-educativo", "faq"),
    )

    disponibles = [
        canal for canal in candidatos
        if canal in permitidos and canal in DESTINOS
    ]

    if not disponibles:
        disponibles = [
            canal for canal in permitidos
            if canal in DESTINOS
        ]

    if not disponibles:
        raise ValueError("No hay destinos Discord autorizados.")

    return rng.choice(disponibles)



def generar_consulta(tema, usados=None, rng=None):
    """Genera conversaciones coherentes con el canal y el tema."""
    if tema not in (*TEMAS, "mixto"):
        raise ValueError("Tema educativo no autorizado")

    if usados is None:
        usados = set()

    if not isinstance(usados, set):
        raise ValueError("El historial debe ser un conjunto")

    rng = rng or random.SystemRandom()
    config = consultar_configuracion()

    canales = [
        canal for canal in config["canales"]
        if canal in DESTINOS and canal in MENSAJES_POR_CANAL
    ]

    if not canales:
        raise ValueError("No hay canales Discord autorizados")

    categorias = tuple(TEMAS) if tema == "mixto" else (tema,)

    # Relacionar cada pregunta dinamica con su categoria real.
    preguntas_por_categoria = {}

    for categoria in categorias:
        for asunto in TEMAS[categoria]:
            for contexto in CONTEXTOS:
                for plantilla in PREGUNTAS:
                    pregunta = plantilla.format(
                        tema=asunto,
                        contexto=contexto,
                    )
                    preguntas_por_categoria[pregunta.casefold()] = categoria

    candidatos = []

    for canal in canales:
        for texto in MENSAJES_POR_CANAL[canal]:
            if texto.casefold() in usados:
                continue

            categoria_real = preguntas_por_categoria.get(texto.casefold())

            if categoria_real is not None:
                candidatos.append((canal, texto, categoria_real))
            elif canal != "foro-educativo":
                # Mensajes comunitarios no tecnicos.
                candidatos.append((canal, texto, tema))
            elif tema == "mixto":
                # Preguntas fijas del foro educativo.
                candidatos.append((canal, texto, "mixto"))

    if not candidatos:
        raise ValueError(
            "Se agotaron las conversaciones disponibles para el tema"
        )

    canal_elegido, pregunta, categoria = rng.choice(candidatos)

    participantes = participantes_activos()
    if not participantes:
        raise ValueError("No hay participantes activos para la simulacion")

    participante = rng.choice(participantes)
    usados.add(pregunta.casefold())

    return {
        "id_simulacion": f"demo_{uuid.uuid4().hex}",
        "autor": participante["nombre"],
        "participante_id": participante["id"],
        "canal": canal_elegido,
        "tema": categoria,
        "texto": pregunta,
        "origen": "discord_demo",
        "es_simulado": True,
        "publicar_discord": False,
    }
