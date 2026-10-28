"""Adaptador Google Cloud Storage para reportes JSON del modulo OCI."""

import json
import os
import re
from pathlib import Path

from google.cloud import storage


PATRON_OBJETO = re.compile(
    r"activos/\d{4}-semana-\d{2}/paquete-distribucion\.json"
)


def obtener_bucket_reportes() -> str:
    bucket = os.getenv(
        "CLOUDEDTECH_REPORTS_GCS_BUCKET", ""
    ).strip()

    if not bucket:
        raise RuntimeError(
            "CLOUDEDTECH_REPORTS_GCS_BUCKET no configurado"
        )

    return bucket


def subir_json_a_gcs(
    ruta_archivo_local: str,
    nombre_objeto_oci: str,
) -> bool:
    """Sube exclusivamente reportes semanales JSON."""
    archivo = Path(ruta_archivo_local).resolve()

    if not archivo.is_file() or archivo.suffix.lower() != ".json":
        raise ValueError("Se requiere un archivo JSON existente")

    if not PATRON_OBJETO.fullmatch(nombre_objeto_oci):
        raise ValueError("Ruta de reporte JSON no permitida")

    with archivo.open("r", encoding="utf-8") as entrada:
        contenido = json.load(entrada)

    if not isinstance(contenido, dict):
        raise ValueError("El reporte debe contener un objeto JSON")

    semana_archivo = archivo.stem
    semana_objeto = nombre_objeto_oci.split("/")[1]

    if semana_archivo != semana_objeto:
        raise ValueError("La semana del archivo no coincide con el destino")

    bucket_name = obtener_bucket_reportes()

    cliente = storage.Client()
    bucket = cliente.bucket(bucket_name)
    objeto = bucket.blob(nombre_objeto_oci)

    objeto.upload_from_filename(
        str(archivo),
        content_type="application/json",
        if_generation_match=0,
    )

    return True
