"""Puente local de preparacion educativa.

No publica mensajes, no realiza solicitudes HTTP y no escribe
en la base de datos. El guardado corresponde al coordinador.
"""

import importlib.util
import sys
from pathlib import Path


def _cargar_modulo(nombre: str, archivo: Path):
    existente = sys.modules.get(nombre)

    if existente is not None:
        origen = getattr(existente, "__file__", None)

        if origen is None or Path(origen).resolve() != archivo.resolve():
            raise RuntimeError(
                "Conflicto de modulo educativo: " + nombre
            )

        return existente

    if not archivo.is_file():
        raise RuntimeError(
            "Modulo educativo no disponible: " + nombre
        )

    spec = importlib.util.spec_from_file_location(
        nombre,
        archivo,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "No se pudo cargar modulo: " + nombre
        )

    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo

    try:
        spec.loader.exec_module(modulo)
    except Exception:
        sys.modules.pop(nombre, None)
        raise

    return modulo


def cargar_dependencias_educativas():
    """Carga exclusivamente los cuatro modulos educativos previstos."""

    motor = Path(__file__).resolve().parents[3] / "motor-ia"

    _cargar_modulo(
        "filtro_mensajes",
        motor / "filtro_mensajes.py",
    )

    _cargar_modulo(
        "clasificador_foro_tecnologico",
        motor / "clasificador_foro_tecnologico.py",
    )

    respuestas = _cargar_modulo(
        "respuestas_foro_tecnologico",
        motor / "respuestas_foro_tecnologico.py",
    )

    identidad = _cargar_modulo(
        "identidad_respuestas_foro",
        motor / "identidad_respuestas_foro.py",
    )

    canales = _cargar_modulo(
        "canales_foro_educativo",
        motor / "canales_foro_educativo.py",
    )

    return {
        "preparar": respuestas.preparar_respuesta,
        "crear_identidad": identidad.identidad_mensaje_discord,
        "canal_autorizado": canales.canal_educativo_autorizado,
    }
