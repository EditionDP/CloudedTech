"""Configuracion persistente de publicacion Discord demo."""

import json
from pathlib import Path
from threading import RLock

# SIETE DESTINOS DISCORD - PASO 3190

RUTA = Path(__file__).with_name(
    "comunidad_demo_publicacion_config.json"
)

BLOQUEO = RLock()

DESTINOS = {
    "general": "1562138937089200242",
    "faq": "1562219960451858443",
    "pqrs": "1562220312177934346",
    "notificaciones": "1562220090437541958",
    "chat-egresados": "1562219605248704592",
    "oportunidades-laborales": "1562220239129809097",
    "foro-educativo": "1563254807479976018",
}

CANALES = tuple(DESTINOS)

PREDETERMINADA = {
    "habilitado": False,
    "canal": "general",
    "canales": ["general"],
    "guild_id": "1562138935948353588",
    "guild_name": "CloudEDTech_OF",
}


def _validar_canales(canales):
    if not isinstance(canales, list):
        raise ValueError("Los canales deben enviarse como lista.")

    if not canales:
        raise ValueError("Seleccione al menos un canal.")

    if any(
        not isinstance(canal, str) or canal not in DESTINOS
        for canal in canales
    ):
        raise ValueError("La seleccion contiene canales no autorizados.")

    if len(set(canales)) != len(canales):
        raise ValueError("No se permiten canales duplicados.")

    return list(canales)


def consultar_configuracion():
    with BLOQUEO:
        resultado = dict(PREDETERMINADA)
        resultado["canales"] = list(PREDETERMINADA["canales"])

        if RUTA.exists():
            datos = json.loads(RUTA.read_text(encoding="utf-8"))

            if not isinstance(datos, dict):
                raise ValueError("Configuracion Discord invalida.")

            resultado.update(datos)

        if not isinstance(resultado["habilitado"], bool):
            raise ValueError("Estado de publicacion invalido.")

        if resultado["guild_id"] != PREDETERMINADA["guild_id"]:
            raise ValueError("Servidor Discord no autorizado.")

        if "canales" not in datos if RUTA.exists() else False:
            resultado["canales"] = [resultado["canal"]]

        resultado["canales"] = _validar_canales(
            resultado["canales"]
        )

        resultado["canal"] = resultado["canales"][0]

        return resultado


def actualizar_configuracion(
    *,
    habilitado=None,
    canal=None,
    canales=None,
):
    with BLOQUEO:
        actual = consultar_configuracion()

        if habilitado is not None:
            if not isinstance(habilitado, bool):
                raise ValueError("Estado de publicacion invalido.")
            actual["habilitado"] = habilitado

        if canal is not None and canales is not None:
            raise ValueError(
                "Utilice canal o canales, no ambos."
            )

        if canales is not None:
            actual["canales"] = _validar_canales(canales)
        elif canal is not None:
            actual["canales"] = _validar_canales([canal])

        actual["canal"] = actual["canales"][0]

        temporal = RUTA.with_suffix(".json.tmp")

        temporal.write_text(
            json.dumps(
                actual,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporal.replace(RUTA)

        return actual
