import sqlite3
from datetime import datetime, timezone

from base_datos import RUTA_BD


def reservar_publicacion_linkedin(
    contenido_id: int,
    author_urn: str,
    tipo_contenido: str,
) -> dict:
    """Reserva un contenido LinkedIn aprobado, sin enviarlo a la API."""
    if contenido_id <= 0:
        raise ValueError("Identificador de contenido invalido.")

    if not author_urn.startswith("urn:li:person:"):
        raise ValueError("Perfil LinkedIn invalido.")

    if tipo_contenido not in {"texto", "texto_imagen", "imagen"}:
        raise ValueError("Modalidad de publicacion invalida.")

    conexion = sqlite3.connect(RUTA_BD, timeout=10)
    conexion.row_factory = sqlite3.Row

    try:
        conexion.execute("BEGIN IMMEDIATE")

        fila = conexion.execute(
            """
            SELECT id, plataforma, estado, estado_publicacion,
                   titulo, contenido, llamada_accion, hashtags,
                   imagen_generada_url
            FROM contenidos_generados
            WHERE id = ?
            """,
            (contenido_id,),
        ).fetchone()

        if fila is None:
            raise LookupError("El contenido no existe.")

        if fila["plataforma"] != "linkedin":
            raise ValueError("El contenido no pertenece a LinkedIn.")

        if fila["estado"] != "aprobado":
            raise ValueError("El contenido debe estar aprobado.")

        if fila["estado_publicacion"] != "no_publicado":
            raise ValueError("El contenido ya tiene un intento de publicacion.")

        ahora = datetime.now(timezone.utc).isoformat()

        cursor = conexion.execute(
            """
            UPDATE contenidos_generados
            SET estado_publicacion = 'enviando',
                intento_publicacion_en = ?,
                error_publicacion = NULL
            WHERE id = ?
              AND plataforma = 'linkedin'
              AND estado = 'aprobado'
              AND estado_publicacion = 'no_publicado'
            """,
            (ahora, contenido_id),
        )

        if cursor.rowcount != 1:
            raise ValueError("No se pudo reservar la publicacion.")

        conexion.commit()

        resultado = dict(fila)
        resultado["author_urn"] = author_urn
        resultado["tipo_contenido_publicacion"] = tipo_contenido

        return resultado

    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()

def confirmar_publicacion_linkedin(
    contenido_id: int,
    author_urn: str,
    tipo_contenido: str,
    post_urn: str,
) -> dict:
    """Confirma un envio real con identificador devuelto por LinkedIn."""
    if contenido_id <= 0:
        raise ValueError("Identificador de contenido invalido.")

    if not author_urn.startswith("urn:li:person:"):
        raise ValueError("Perfil LinkedIn invalido.")

    if tipo_contenido not in {"texto", "texto_imagen", "imagen"}:
        raise ValueError("Modalidad invalida.")

    if not post_urn.startswith(("urn:li:share:", "urn:li:ugcPost:")):
        raise ValueError("Identificador de publicacion LinkedIn invalido.")

    ahora = datetime.now(timezone.utc).isoformat()
    conexion = sqlite3.connect(RUTA_BD, timeout=10)

    try:
        conexion.execute("BEGIN IMMEDIATE")

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS publicaciones_linkedin (
                contenido_id INTEGER PRIMARY KEY,
                author_urn TEXT NOT NULL,
                tipo_contenido TEXT NOT NULL,
                post_urn TEXT NOT NULL UNIQUE,
                publicado_en TEXT NOT NULL,
                FOREIGN KEY (contenido_id)
                    REFERENCES contenidos_generados(id)
            )
            """
        )

        cursor = conexion.execute(
            """
            UPDATE contenidos_generados
            SET estado_publicacion = 'publicado',
                publicado_en = ?,
                error_publicacion = NULL
            WHERE id = ?
              AND plataforma = 'linkedin'
              AND estado = 'aprobado'
              AND estado_publicacion IN (
                  'enviando',
                  'resultado_desconocido'
              )
            """,
            (ahora, contenido_id),
        )

        if cursor.rowcount != 1:
            raise ValueError("No se pudo confirmar la publicacion.")

        conexion.execute(
            """
            INSERT INTO publicaciones_linkedin (
                contenido_id,
                author_urn,
                tipo_contenido,
                post_urn,
                publicado_en
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                contenido_id,
                author_urn,
                tipo_contenido,
                post_urn,
                ahora,
            ),
        )

        conexion.commit()

        return {
            "id": contenido_id,
            "plataforma": "linkedin",
            "estado_publicacion": "publicado",
            "author_urn": author_urn,
            "tipo_contenido": tipo_contenido,
            "post_urn": post_urn,
            "publicado_en": ahora,
        }

    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def marcar_resultado_desconocido_linkedin(
    contenido_id: int,
    detalle: str,
) -> bool:
    """Bloquea reintentos cuando el resultado del envio es incierto."""
    with sqlite3.connect(RUTA_BD, timeout=10) as conexion:
        cursor = conexion.execute(
            """
            UPDATE contenidos_generados
            SET estado_publicacion = 'resultado_desconocido',
                error_publicacion = ?
            WHERE id = ?
              AND plataforma = 'linkedin'
              AND estado_publicacion = 'enviando'
            """,
            (detalle[:500], contenido_id),
        )
        return cursor.rowcount == 1


def liberar_reserva_linkedin_sin_envio(
    contenido_id: int,
) -> bool:
    """Usar solo si NO se invoco la API de publicacion LinkedIn."""
    with sqlite3.connect(RUTA_BD, timeout=10) as conexion:
        cursor = conexion.execute(
            """
            UPDATE contenidos_generados
            SET estado_publicacion = 'no_publicado',
                intento_publicacion_en = NULL,
                error_publicacion = NULL
            WHERE id = ?
              AND plataforma = 'linkedin'
              AND estado_publicacion = 'enviando'
            """,
            (contenido_id,),
        )
        return cursor.rowcount == 1

def reservar_intento_linkedin(
    contenido_id: int,
    author_urn: str,
    tipo_contenido: str,
) -> dict:
    """Reserva y registra un intento LinkedIn en una sola transaccion."""
    import uuid

    if contenido_id <= 0:
        raise ValueError("Identificador de contenido invalido.")

    if not (
        isinstance(author_urn, str)
        and author_urn.startswith("urn:li:person:")
        and len(author_urn) > len("urn:li:person:")
    ):
        raise ValueError("Perfil LinkedIn invalido.")

    if tipo_contenido not in {"texto", "texto_imagen", "imagen"}:
        raise ValueError("Modalidad invalida.")

    intento_id = uuid.uuid4().hex
    ahora = datetime.now(timezone.utc).isoformat()

    conexion = sqlite3.connect(RUTA_BD, timeout=10)
    conexion.row_factory = sqlite3.Row

    try:
        conexion.execute("BEGIN IMMEDIATE")

        fila = conexion.execute(
            """
            SELECT id, plataforma, estado, estado_publicacion,
                   titulo, contenido, llamada_accion, hashtags,
                   imagen_generada_url
            FROM contenidos_generados
            WHERE id = ?
            """,
            (contenido_id,),
        ).fetchone()

        if fila is None:
            raise LookupError("El contenido no existe.")

        if fila["plataforma"] != "linkedin":
            raise ValueError("El contenido no pertenece a LinkedIn.")

        if fila["estado"] != "aprobado":
            raise ValueError("El contenido debe estar aprobado.")

        if fila["estado_publicacion"] != "no_publicado":
            raise ValueError("El contenido ya tiene un intento de publicacion.")

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS intentos_publicacion_linkedin (
                intento_id TEXT PRIMARY KEY,
                contenido_id INTEGER NOT NULL UNIQUE,
                author_urn TEXT NOT NULL,
                tipo_contenido TEXT NOT NULL,
                creado_en TEXT NOT NULL,
                post_urn TEXT,
                FOREIGN KEY (contenido_id)
                    REFERENCES contenidos_generados(id)
            )
            """
        )

        cursor = conexion.execute(
            """
            UPDATE contenidos_generados
            SET estado_publicacion = 'enviando',
                intento_publicacion_en = ?,
                error_publicacion = NULL
            WHERE id = ?
              AND plataforma = 'linkedin'
              AND estado = 'aprobado'
              AND estado_publicacion = 'no_publicado'
            """,
            (ahora, contenido_id),
        )

        if cursor.rowcount != 1:
            raise ValueError("No se pudo reservar la publicacion.")

        conexion.execute(
            """
            INSERT INTO intentos_publicacion_linkedin (
                intento_id, contenido_id, author_urn,
                tipo_contenido, creado_en
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                intento_id,
                contenido_id,
                author_urn,
                tipo_contenido,
                ahora,
            ),
        )

        conexion.commit()

        resultado = dict(fila)
        resultado["intento_id"] = intento_id
        resultado["author_urn"] = author_urn
        resultado["tipo_contenido_publicacion"] = tipo_contenido

        return resultado

    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()

def confirmar_intento_linkedin(
    contenido_id: int,
    intento_id: str,
    author_urn: str,
    tipo_contenido: str,
    post_urn: str,
) -> dict:
    """Confirma solo el intento reservado y el post real recibido."""
    if contenido_id <= 0:
        raise ValueError("Identificador de contenido invalido.")

    if not intento_id or len(intento_id) != 32:
        raise ValueError("Identificador de intento invalido.")

    if not post_urn.startswith(("urn:li:share:", "urn:li:ugcPost:")):
        raise ValueError("Identificador de publicacion LinkedIn invalido.")

    ahora = datetime.now(timezone.utc).isoformat()
    conexion = sqlite3.connect(RUTA_BD, timeout=10)
    conexion.row_factory = sqlite3.Row

    try:
        conexion.execute("BEGIN IMMEDIATE")

        intento = conexion.execute(
            """
            SELECT intento_id, contenido_id, author_urn,
                   tipo_contenido, post_urn
            FROM intentos_publicacion_linkedin
            WHERE intento_id = ?
              AND contenido_id = ?
            """,
            (intento_id, contenido_id),
        ).fetchone()

        if intento is None:
            raise ValueError("No existe una reserva para este intento.")

        if intento["author_urn"] != author_urn:
            raise ValueError("El perfil no coincide con la reserva.")

        if intento["tipo_contenido"] != tipo_contenido:
            raise ValueError("La modalidad no coincide con la reserva.")

        if intento["post_urn"] is not None:
            raise ValueError("Este intento ya fue confirmado.")

        cursor = conexion.execute(
            """
            UPDATE contenidos_generados
            SET estado_publicacion = 'publicado',
                publicado_en = ?,
                error_publicacion = NULL
            WHERE id = ?
              AND plataforma = 'linkedin'
              AND estado = 'aprobado'
              AND estado_publicacion IN (
                  'enviando',
                  'resultado_desconocido'
              )
            """,
            (ahora, contenido_id),
        )

        if cursor.rowcount != 1:
            raise ValueError("No se pudo confirmar el estado del contenido.")

        conexion.execute(
            """
            UPDATE intentos_publicacion_linkedin
            SET post_urn = ?
            WHERE intento_id = ?
              AND post_urn IS NULL
            """,
            (post_urn, intento_id),
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS publicaciones_linkedin (
                contenido_id INTEGER PRIMARY KEY,
                author_urn TEXT NOT NULL,
                tipo_contenido TEXT NOT NULL,
                post_urn TEXT NOT NULL UNIQUE,
                publicado_en TEXT NOT NULL,
                FOREIGN KEY (contenido_id)
                    REFERENCES contenidos_generados(id)
            )
            """
        )

        conexion.execute(
            """
            INSERT INTO publicaciones_linkedin (
                contenido_id,
                author_urn,
                tipo_contenido,
                post_urn,
                publicado_en
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                contenido_id,
                author_urn,
                tipo_contenido,
                post_urn,
                ahora,
            ),
        )

        conexion.commit()

        return {
            "id": contenido_id,
            "plataforma": "linkedin",
            "estado_publicacion": "publicado",
            "intento_id": intento_id,
            "author_urn": author_urn,
            "tipo_contenido": tipo_contenido,
            "post_urn": post_urn,
            "publicado_en": ahora,
        }

    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()

def marcar_intento_linkedin_desconocido(
    contenido_id: int,
    intento_id: str,
    detalle: str,
) -> bool:
    """Conserva el bloqueo si el resultado del envio es incierto."""
    conexion = sqlite3.connect(RUTA_BD, timeout=10)

    try:
        conexion.execute("BEGIN IMMEDIATE")

        cursor = conexion.execute(
            """
            UPDATE contenidos_generados
            SET estado_publicacion = 'resultado_desconocido',
                error_publicacion = ?
            WHERE id = ?
              AND plataforma = 'linkedin'
              AND estado_publicacion = 'enviando'
              AND EXISTS (
                  SELECT 1
                  FROM intentos_publicacion_linkedin
                  WHERE intento_id = ?
                    AND contenido_id = ?
                    AND post_urn IS NULL
              )
            """,
            (str(detalle)[:500], contenido_id, intento_id, contenido_id),
        )

        conexion.commit()
        return cursor.rowcount == 1

    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def liberar_intento_linkedin_sin_envio(
    contenido_id: int,
    intento_id: str,
) -> bool:
    """Libera exclusivamente un intento cuya API nunca fue invocada."""
    conexion = sqlite3.connect(RUTA_BD, timeout=10)

    try:
        conexion.execute("BEGIN IMMEDIATE")

        cursor = conexion.execute(
            """
            UPDATE contenidos_generados
            SET estado_publicacion = 'no_publicado',
                intento_publicacion_en = NULL,
                error_publicacion = NULL
            WHERE id = ?
              AND plataforma = 'linkedin'
              AND estado_publicacion = 'enviando'
              AND EXISTS (
                  SELECT 1
                  FROM intentos_publicacion_linkedin
                  WHERE intento_id = ?
                    AND contenido_id = ?
                    AND post_urn IS NULL
              )
            """,
            (contenido_id, intento_id, contenido_id),
        )

        if cursor.rowcount == 1:
            conexion.execute(
                """
                DELETE FROM intentos_publicacion_linkedin
                WHERE intento_id = ?
                  AND contenido_id = ?
                  AND post_urn IS NULL
                """,
                (intento_id, contenido_id),
            )

        conexion.commit()
        return cursor.rowcount == 1

    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()