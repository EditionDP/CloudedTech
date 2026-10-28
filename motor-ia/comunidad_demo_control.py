"""Contrato seguro de control para comunidad simulada.

No ejecuta tareas, no modifica bases de datos y no publica en Discord.
"""

from comunidad_demo_config import validar_configuracion


ACCIONES_PERMITIDAS = (
    "iniciar",
    "detener",
    "estado",
)


def validar_orden_simulacion(accion, tema="mixto", ritmo="medio"):
    if accion not in ACCIONES_PERMITIDAS:
        raise ValueError("Accion de simulacion no autorizada")

    configuracion = validar_configuracion(tema, ritmo)

    return {
        "accion": accion,
        "tema": configuracion["tema"],
        "ritmo": configuracion["ritmo"],
        "intervalo_minimo_segundos": configuracion[
            "intervalo_minimo_segundos"
        ],
        "intervalo_maximo_segundos": configuracion[
            "intervalo_maximo_segundos"
        ],
        "origen_comunidad": "discord_demo",
        "es_simulado": True,
        "publicar_discord": False,
    }


def estado_inicial_simulacion():
    return {
        "estado": "detenido",
        "tema": "mixto",
        "ritmo": "medio",
        "participantes": 50,
        "mensajes_generados": 0,
        "origen_comunidad": "discord_demo",
        "es_simulado": True,
        "publicar_discord": False,
    }
