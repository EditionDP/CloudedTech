"""Estado en memoria del simulador de comunidad.

No genera mensajes, no modifica bases de datos y no publica en Discord.
"""

from copy import deepcopy
from threading import Lock

from comunidad_demo_control import (
    estado_inicial_simulacion,
    validar_orden_simulacion,
)


_bloqueo = Lock()
_estado = estado_inicial_simulacion()


def consultar_estado():
    with _bloqueo:
        return deepcopy(_estado)


def iniciar_simulacion(tema="mixto", ritmo="medio"):
    configuracion = validar_orden_simulacion(
        "iniciar",
        tema=tema,
        ritmo=ritmo,
    )

    with _bloqueo:
        if _estado["estado"] == "ejecutando":
            return {
                "cambio_realizado": False,
                "motivo": "simulacion_ya_iniciada",
                "estado": deepcopy(_estado),
            }

        _estado.update({
            "estado": "ejecutando",
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
        })

        return {
            "cambio_realizado": True,
            "motivo": "simulacion_iniciada",
            "estado": deepcopy(_estado),
        }


def detener_simulacion():
    with _bloqueo:
        if _estado["estado"] == "detenido":
            return {
                "cambio_realizado": False,
                "motivo": "simulacion_ya_detenida",
                "estado": deepcopy(_estado),
            }

        _estado["estado"] = "detenido"

        return {
            "cambio_realizado": True,
            "motivo": "simulacion_detenida",
            "estado": deepcopy(_estado),
        }
