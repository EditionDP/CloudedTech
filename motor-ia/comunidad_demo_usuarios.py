"""Catalogo de participantes de la comunidad demostrativa.

Estos perfiles son sinteticos para pruebas de CloudEdTech.
No representan cuentas autenticadas de Discord.
"""

USUARIOS_EQUIPO = (
    "amartinezb",
    "eramirez",
    "aramirez",
    "egarcia",
    "pmadrid",
    "ffraustro",
    "mmarquez",
    "fvillaverde",
    "msierra",
    "elopez",
    "torante",
    "castudillo",
)

USUARIOS_COMMUNITY = tuple(
    f"usuario community {numero}"
    for numero in range(1, 39)
)

PARTICIPANTES_DEMO = (
    USUARIOS_EQUIPO + USUARIOS_COMMUNITY
)

ORIGEN_DEMO = "discord_demo"


def obtener_participantes():
    """Devuelve los participantes sin modificar el catalogo."""
    return list(PARTICIPANTES_DEMO)


def obtener_perfil(numero):
    """Obtiene un participante por posicion, comenzando en cero."""
    if not isinstance(numero, int) or isinstance(numero, bool):
        raise ValueError("Indice de participante invalido")

    if numero < 0 or numero >= len(PARTICIPANTES_DEMO):
        raise ValueError("Participante fuera de rango")

    return {
        "id": f"demo_user_{numero + 1:03d}",
        "nombre": PARTICIPANTES_DEMO[numero],
        "origen": ORIGEN_DEMO,
        "es_simulado": True,
    }
