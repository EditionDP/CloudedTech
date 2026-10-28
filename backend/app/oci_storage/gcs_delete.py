"""Eliminacion controlada de reportes JSON en Google Cloud Storage."""

import os
import re

from google.cloud import storage


PATRON_REPORTE = re.compile(
    r"activos/\d{4}-semana-\d{2}/paquete-distribucion\.json"
)


def validar_objeto_reporte(object_name: str) -> str:
    if not isinstance(object_name, str):
        raise ValueError("Nombre de objeto invalido")

    if not PATRON_REPORTE.fullmatch(object_name):
        raise ValueError("La ruta no corresponde a un reporte semanal")

    return object_name


def obtener_bucket_reportes() -> str:
    nombre = os.getenv(
        "CLOUDEDTECH_REPORTS_GCS_BUCKET", ""
    ).strip()

    if not nombre:
        raise RuntimeError(
            "CLOUDEDTECH_REPORTS_GCS_BUCKET no configurado"
        )

    return nombre


def eliminar_reporte_gcs(object_name: str) -> bool:
    """Elimina una version existente de un reporte semanal JSON."""
    nombre_validado = validar_objeto_reporte(object_name)
    bucket_name = obtener_bucket_reportes()

    cliente = storage.Client()
    bucket = cliente.bucket(bucket_name)
    objeto = bucket.get_blob(nombre_validado)

    if objeto is None:
        return False

    if objeto.generation is None:
        raise RuntimeError(
            "No se pudo identificar la generacion del objeto"
        )

    objeto.delete(
        if_generation_match=int(objeto.generation)
    )

    return True
