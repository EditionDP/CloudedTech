"""
Metricas de mensajes unicos del foro.

Distingue actividad real y simulada.
No escribe bases de datos ni publica mensajes.
"""

ORIGEN_DEMO = "discord_demo"
ORIGEN_PRUEBA = "TEST_INTEGRACION_MERGE"


def calcular_interacciones_foro(
    interacciones,
    canales_reales=None,
    canales_demo=None,
):
    if not isinstance(interacciones, list):
        raise ValueError("Interacciones invalidas")

    canales_reales = set(canales_reales or [])
    canales_demo = set(
        canales_demo or ["cloudedtech_demo_preguntas"]
    )

    reales = set()
    simuladas = set()

    for item in interacciones:
        if not isinstance(item, dict):
            continue

        origen = item.get("origen_comunidad")
        canal_id = str(item.get("channel_id") or "")
        mensaje_id = str(item.get("message_id") or "")

        if not canal_id or not mensaje_id:
            continue

        if origen == ORIGEN_PRUEBA:
            continue

        clave = (canal_id, mensaje_id)

        if origen == ORIGEN_DEMO:
            if canal_id in canales_demo:
                simuladas.add(clave)
            continue

        # Sin identificadores de canales reales autorizados
        # no se clasifican mensajes como foro real.
        if (
            origen == "discord"
            and canal_id in canales_reales
        ):
            reales.add(clave)

    return {
        "total": len(reales) + len(simuladas),
        "discord_real": len(reales),
        "comunidad_simulada": len(simuladas),
        "criterio": "mensajes_unicos",
    }
