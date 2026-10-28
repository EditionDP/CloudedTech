"""Configuracion segura del simulador Community.

No inicia tareas, no publica mensajes y no modifica bases de datos.
"""

TEMAS_PERMITIDOS = (
    "ia",
    "programacion",
    "ciberseguridad",
    "datos",
    "mixto",
)

RITMOS_PERMITIDOS = {
    "bajo": (60, 120),
    "medio": (20, 60),
    "alto": (5, 20),
}

ESTADO_INICIAL = "detenido"
ORIGEN_SIMULACION = "discord_demo"


def validar_configuracion(tema, ritmo):
    if tema not in TEMAS_PERMITIDOS:
        raise ValueError("Tema de simulacion no autorizado")

    if ritmo not in RITMOS_PERMITIDOS:
        raise ValueError("Ritmo de simulacion no autorizado")

    minimo, maximo = RITMOS_PERMITIDOS[ritmo]

    return {
        "tema": tema,
        "ritmo": ritmo,
        "intervalo_minimo_segundos": minimo,
        "intervalo_maximo_segundos": maximo,
        "estado": ESTADO_INICIAL,
        "origen": ORIGEN_SIMULACION,
        "publicar_discord": False,
    }
