import json
import os

import oci

from app.oci_storage.config import get_oci_settings


def _get_client():
    settings = get_oci_settings()

    config_file = settings["config_file"]
    if not config_file:
        raise RuntimeError("OCI_CONFIG_FILE no configurado")

    config = oci.config.from_file(
        file_location=os.path.expanduser(config_file),
        profile_name=settings["config_profile"],
    )

    client = oci.object_storage.ObjectStorageClient(config)

    namespace = settings["namespace"] or client.get_namespace().data
    bucket = settings["bucket_name"]

    if not bucket:
        raise RuntimeError("OCI_BUCKET_NAME no configurado")

    return client, namespace, bucket


def _list_oci_json_objects(prefix: str = "", limit: int = 100):
    client, namespace, bucket = _get_client()

    response = client.list_objects(
        namespace_name=namespace,
        bucket_name=bucket,
        prefix=prefix,
        limit=limit,
    )

    return [
        {
            "name": obj.name,
            "size": obj.size,
            "time_created": (
                obj.time_created.isoformat()
                if obj.time_created
                else None
            ),
        }
        for obj in response.data.objects
        if obj.name.lower().endswith(".json")
    ]


def _get_oci_json_object(object_name: str):
    if not object_name.lower().endswith(".json"):
        raise ValueError("Solo se permiten archivos JSON")

    client, namespace, bucket = _get_client()

    response = client.get_object(
        namespace_name=namespace,
        bucket_name=bucket,
        object_name=object_name,
    )

    return json.loads(response.data.content.decode("utf-8"))


def _storage_provider() -> str:
    provider = os.getenv(
        "CLOUDEDTECH_STORAGE_PROVIDER", "local"
    ).strip().lower()

    if provider not in {"local", "oci", "gcs"}:
        raise RuntimeError("Proveedor de almacenamiento no soportado")

    return provider


def _gcs_bucket():
    from google.cloud import storage

    bucket_name = os.getenv(
        "CLOUDEDTECH_REPORTS_GCS_BUCKET", ""
    ).strip()

    if not bucket_name:
        raise RuntimeError(
            "CLOUDEDTECH_REPORTS_GCS_BUCKET no configurado"
        )

    client = storage.Client()
    return client.bucket(bucket_name)


def _list_gcs_json_objects(prefix: str = "", limit: int = 100):
    if not isinstance(prefix, str) or ".." in prefix:
        raise ValueError("Prefijo de consulta no permitido")

    bucket = _gcs_bucket()
    objects = bucket.list_blobs(
        prefix=prefix,
        max_results=limit,
    )

    return [
        {
            "name": obj.name,
            "size": obj.size,
            "time_created": (
                obj.time_created.isoformat()
                if obj.time_created
                else None
            ),
        }
        for obj in objects
        if obj.name.lower().endswith(".json")
    ]


def _get_gcs_json_object(object_name: str):
    if not isinstance(object_name, str):
        raise ValueError("Nombre de objeto no valido")

    if (
        not object_name.lower().endswith(".json")
        or ".." in object_name
        or object_name.startswith("/")
    ):
        raise ValueError("Solo se permiten objetos JSON validos")

    bucket = _gcs_bucket()
    blob = bucket.blob(object_name)
    contenido = blob.download_as_bytes()

    return json.loads(contenido.decode("utf-8"))


def list_json_objects(prefix: str = "", limit: int = 100):
    provider = _storage_provider()

    if provider == "gcs":
        return _list_gcs_json_objects(prefix, limit)

    if provider == "oci":
        return _list_oci_json_objects(prefix, limit)

    raise RuntimeError(
        "Almacenamiento remoto no configurado"
    )


def get_json_object(object_name: str):
    provider = _storage_provider()

    if provider == "gcs":
        return _get_gcs_json_object(object_name)

    if provider == "oci":
        return _get_oci_json_object(object_name)

    raise RuntimeError(
        "Almacenamiento remoto no configurado"
    )
