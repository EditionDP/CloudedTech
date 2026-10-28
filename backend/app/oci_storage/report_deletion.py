"""Coordinacion de eliminacion de reportes semanales."""

import os
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.oci_storage.gcs_delete import eliminar_reporte_gcs
from app.oci_storage.models import OCIWeeklySync
from app.oci_storage.motor_bridge import MOTOR_REPORTS_PREFIX
from app.content_workflow.service import solicitar_motor


PATRON_SEMANA = re.compile(r"\\d{4}-semana-\\d{2}")


def eliminar_reporte_semanal(
    semana: str,
    db: Session,
) -> dict:
    if not PATRON_SEMANA.fullmatch(semana):
        raise HTTPException(
            status_code=400,
            detail="Identificador de semana invalido",
        )

    from datetime import date, timedelta
    from app.oci_storage.service import get_existing_weekly_sync

    anio = int(semana[:4])
    numero = int(semana[-2:])

    if numero < 1:
        raise HTTPException(
            status_code=400,
            detail="Numero de semana invalido",
        )

    inicio = date(2026, 9, 21) + timedelta(weeks=numero - 1)
    fin = inicio + timedelta(days=6)

    if inicio.year != anio:
        raise HTTPException(
            status_code=400,
            detail="Semana fuera del periodo del proyecto",
        )

    registro = get_existing_weekly_sync(db, inicio, fin)

    # No eliminar registros con operaciones pendientes o estados
    # desconocidos. Requieren conciliacion antes de continuar.
    if registro is not None and registro.status not in {
        "synced",
        "saved_locally",
        "delete_pending_local",
    }:
        raise HTTPException(
            status_code=409,
            detail=(
                "El reporte tiene una sincronizacion pendiente "
                "o un estado que requiere revision"
            ),
        )

    # Si no hay registro SQL, no podemos demostrar que el reporte
    # no existe tambien en almacenamiento remoto.
    if registro is None:
        raise HTTPException(
            status_code=409,
            detail=(
                "No existe registro de sincronizacion para este "
                "reporte. Se requiere conciliacion previa."
            ),
        )

    proveedor = os.getenv(
        "CLOUDEDTECH_STORAGE_PROVIDER", "local"
    ).strip().lower()

    eliminado_remotamente = False

    if registro and registro.status == "synced":
        if proveedor != "gcs":
            raise HTTPException(
                status_code=409,
                detail=(
                    "No se puede eliminar un reporte sincronizado "
                    "sin configurar Google Cloud Storage"
                ),
            )

        objeto = (
            f"activos/{semana}/paquete-distribucion.json"
        )

        try:
            eliminado_remotamente = eliminar_reporte_gcs(objeto)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="No se pudo eliminar el reporte remoto",
            ) from exc

    try:
        resultado_motor = solicitar_motor(
            "DELETE",
            f"{MOTOR_REPORTS_PREFIX}/reports/{semana}",
        )
    except Exception as exc:
        # Conservar un estado recuperable cuando Google ya elimino
        # el objeto, pero la eliminacion local no fue confirmada.
        if eliminado_remotamente and registro is not None:
            try:
                registro.status = "delete_pending_local"
                db.commit()
            except Exception:
                db.rollback()
                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Eliminacion remota realizada, pero no fue "
                        "posible registrar el estado pendiente. "
                        "Se requiere revision administrativa."
                    ),
                ) from exc

        raise HTTPException(
            status_code=503,
            detail=(
                "No se pudo completar la eliminacion local. "
                "Es necesario revisar el estado del reporte."
            ),
        ) from exc

    if resultado_motor.get("deleted_locally") is not True:
        raise HTTPException(
            status_code=502,
            detail="El Motor IA no confirmo la eliminacion",
        )

    if registro is not None:
        try:
            db.delete(registro)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=503,
                detail="No se pudo actualizar el historial del reporte",
            )

    return {
        "status": "deleted",
        "semana": semana,
        "deleted_locally": True,
        "deleted_remotely": eliminado_remotamente,
        "message": "Reporte eliminado correctamente",
    }
