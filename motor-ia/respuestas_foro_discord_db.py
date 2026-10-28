"""Control persistente de respuestas automaticas del foro Discord."""

import sqlite3
from datetime import datetime, timezone

from base_datos import RUTA_BD


def _ahora():
    return datetime.now(timezone.utc).isoformat()


def reservar_respuesta(mensaje_id, hilo_id, servidor_id):
    """Reserva una sola vez un mensaje. Nunca reintenta automaticamente."""
    with sqlite3.connect(str(RUTA_BD), timeout=15) as conexion:
        conexion.execute("BEGIN IMMEDIATE")

        existente = conexion.execute(
            "SELECT estado FROM respuestas_foro_discord WHERE mensaje_id = ?",
            (str(mensaje_id),),
        ).fetchone()

        if existente:
            conexion.commit()
            return False

        ahora = _ahora()

        conexion.execute(
            """
            INSERT INTO respuestas_foro_discord (
                mensaje_id, hilo_id, servidor_id, estado,
                creado_en, actualizado_en
            )
            VALUES (?, ?, ?, 'enviando', ?, ?)
            """,
            (str(mensaje_id), str(hilo_id), str(servidor_id), ahora, ahora),
        )

        conexion.commit()
        return True


def confirmar_respuesta(mensaje_id, respuesta_id, respuesta_texto):
    if not respuesta_id:
        raise ValueError("El ID de la respuesta es obligatorio.")

    with sqlite3.connect(str(RUTA_BD), timeout=15) as conexion:
        conexion.execute("BEGIN IMMEDIATE")

        ahora = _ahora()

        cursor = conexion.execute(
            """
            UPDATE respuestas_foro_discord
            SET estado = 'publicado',
                respuesta_id = ?,
                respuesta_texto = ?,
                error = NULL,
                actualizado_en = ?,
                publicado_en = ?
            WHERE mensaje_id = ?
              AND estado IN ('enviando', 'resultado_desconocido')
            """,
            (
                str(respuesta_id),
                respuesta_texto,
                ahora,
                ahora,
                str(mensaje_id),
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError("No existe una reserva valida para confirmar.")

        conexion.commit()


def marcar_error_respuesta(mensaje_id, detalle):
    """Registra el fallo sin habilitar reintentos automaticos."""
    with sqlite3.connect(str(RUTA_BD), timeout=15) as conexion:
        conexion.execute(
            """
            UPDATE respuestas_foro_discord
            SET estado = 'error',
                error = ?,
                actualizado_en = ?
            WHERE mensaje_id = ?
              AND estado = 'enviando'
            """,
            (str(detalle)[:1000], _ahora(), str(mensaje_id)),
        )
        conexion.commit()


def marcar_resultado_desconocido(mensaje_id, detalle):
    """Bloquea duplicados cuando el resultado del envio es incierto."""
    with sqlite3.connect(str(RUTA_BD), timeout=15) as conexion:
        conexion.execute(
            """
            UPDATE respuestas_foro_discord
            SET estado = 'resultado_desconocido',
                error = ?,
                actualizado_en = ?
            WHERE mensaje_id = ?
              AND estado = 'enviando'
            """,
            (str(detalle)[:1000], _ahora(), str(mensaje_id)),
        )
        conexion.commit()
