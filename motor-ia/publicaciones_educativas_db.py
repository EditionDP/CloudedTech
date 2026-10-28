import sqlite3
from pathlib import Path

from base_datos import RUTA_BD


PLATAFORMAS = ("discord", "x", "linkedin")


def inicializar_publicaciones_educativas() -> None:
    """Crea las tablas educativas sin modificar contenidos existentes."""

    conexion = sqlite3.connect(RUTA_BD, timeout=10)

    try:
        conexion.execute("BEGIN IMMEDIATE")

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS publicaciones_educativas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tema TEXT NOT NULL,
                titulo TEXT NOT NULL,
                contenido TEXT NOT NULL,
                responsable TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                creado_en TEXT NOT NULL,
                actualizado_en TEXT NOT NULL
            )
            """
        )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS publicaciones_educativas_destinos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publicacion_id INTEGER NOT NULL,
                plataforma TEXT NOT NULL
                    CHECK (plataforma IN ('discord', 'x', 'linkedin')),
                estado TEXT NOT NULL DEFAULT 'pendiente'
                    CHECK (
                        estado IN (
                            'pendiente',
                            'enviando',
                            'publicado',
                            'error',
                            'resultado_desconocido',
                            'pendiente_conexion'
                        )
                    ),
                identificador_externo TEXT,
                url_publicacion TEXT,
                intento_en TEXT,
                publicado_en TEXT,
                error TEXT,
                creado_en TEXT NOT NULL,
                actualizado_en TEXT NOT NULL,
                FOREIGN KEY (publicacion_id)
                    REFERENCES publicaciones_educativas(id),
                UNIQUE (publicacion_id, plataforma)
            )
            """
        )

        conexion.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_publicaciones_educativas_destinos_estado
            ON publicaciones_educativas_destinos (
                plataforma,
                estado
            )
            """
        )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def registrar_publicacion_educativa(
    tema: str,
    titulo: str,
    contenido: str,
    responsable: str,
) -> dict:
    """Registra una publicación educativa y sus tres destinos."""

    from datetime import datetime, timezone

    tema = tema.strip().lower()
    titulo = titulo.strip()
    contenido = contenido.strip()
    responsable = responsable.strip()

    temas_permitidos = {
        "api",
        "python",
        "sql",
        "inteligencia artificial",
        "docker",
        "postgresql",
        "ciberseguridad",
        "react",
    }

    if tema not in temas_permitidos:
        raise ValueError("Tema educativo no autorizado.")

    if not titulo or not contenido or not responsable:
        raise ValueError(
            "El título, contenido y responsable son obligatorios."
        )

    if len(titulo) > 200:
        raise ValueError("El título supera 200 caracteres.")

    if len(contenido) > 10000:
        raise ValueError("El contenido supera 10000 caracteres.")

    ahora = datetime.now(timezone.utc).isoformat()

    conexion = sqlite3.connect(RUTA_BD, timeout=10)
    conexion.row_factory = sqlite3.Row

    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute("BEGIN IMMEDIATE")

        cursor = conexion.execute(
            """
            INSERT INTO publicaciones_educativas (
                tema,
                titulo,
                contenido,
                responsable,
                version,
                creado_en,
                actualizado_en
            )
            VALUES (?, ?, ?, ?, 1, ?, ?)
            """,
            (
                tema,
                titulo,
                contenido,
                responsable,
                ahora,
                ahora,
            ),
        )

        publicacion_id = cursor.lastrowid

        for plataforma in PLATAFORMAS:
            conexion.execute(
                """
                INSERT INTO publicaciones_educativas_destinos (
                    publicacion_id,
                    plataforma,
                    estado,
                    creado_en,
                    actualizado_en
                )
                VALUES (?, ?, 'pendiente', ?, ?)
                """,
                (
                    publicacion_id,
                    plataforma,
                    ahora,
                    ahora,
                ),
            )

        conexion.commit()

        return obtener_publicacion_educativa(publicacion_id)

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def obtener_publicacion_educativa(
    publicacion_id: int,
) -> dict | None:
    """Consulta una publicación y los estados de sus destinos."""

    if publicacion_id <= 0:
        raise ValueError("Identificador inválido.")

    conexion = sqlite3.connect(RUTA_BD, timeout=10)
    conexion.row_factory = sqlite3.Row

    try:
        fila = conexion.execute(
            """
            SELECT *
            FROM publicaciones_educativas
            WHERE id = ?
            """,
            (publicacion_id,),
        ).fetchone()

        if fila is None:
            return None

        destinos = conexion.execute(
            """
            SELECT
                plataforma,
                estado,
                identificador_externo,
                url_publicacion,
                intento_en,
                publicado_en,
                error
            FROM publicaciones_educativas_destinos
            WHERE publicacion_id = ?
            ORDER BY CASE plataforma
                WHEN 'discord' THEN 1
                WHEN 'x' THEN 2
                WHEN 'linkedin' THEN 3
                ELSE 4
            END
            """,
            (publicacion_id,),
        ).fetchall()

        resultado = dict(fila)
        resultado["destinos"] = [
            dict(destino)
            for destino in destinos
        ]

        return resultado

    finally:
        conexion.close()


def reservar_destino_educativo(
    publicacion_id: int,
    plataforma: str,
) -> dict:
    """
    Reserva atomicamente un destino educativo.

    Solo permite estados pendiente o error.
    No realiza publicaciones externas.
    """

    from datetime import datetime, timezone

    if not isinstance(publicacion_id, int) or isinstance(
        publicacion_id, bool
    ) or publicacion_id <= 0:
        raise ValueError("Identificador de publicacion invalido.")

    if not isinstance(plataforma, str):
        raise ValueError("Plataforma invalida.")

    plataforma = plataforma.strip().lower()

    if plataforma not in PLATAFORMAS:
        raise ValueError("Plataforma no autorizada.")

    ahora = datetime.now(timezone.utc).isoformat()

    conexion = sqlite3.connect(RUTA_BD, timeout=10)
    conexion.row_factory = sqlite3.Row

    try:
        conexion.execute("BEGIN IMMEDIATE")

        fila = conexion.execute(
            """
            SELECT
                p.id,
                p.tema,
                p.titulo,
                p.contenido,
                p.version,
                d.plataforma,
                d.estado
            FROM publicaciones_educativas AS p
            JOIN publicaciones_educativas_destinos AS d
              ON d.publicacion_id = p.id
            WHERE p.id = ?
              AND d.plataforma = ?
            """,
            (publicacion_id, plataforma),
        ).fetchone()

        if fila is None:
            raise LookupError(
                "La publicacion o el destino no existe."
            )

        if fila["estado"] not in ("pendiente", "error"):
            raise ValueError(
                "El destino no permite un nuevo intento de envio."
            )

        cursor = conexion.execute(
            """
            UPDATE publicaciones_educativas_destinos
            SET estado = 'enviando',
                intento_en = ?,
                actualizado_en = ?,
                error = NULL
            WHERE publicacion_id = ?
              AND plataforma = ?
              AND estado IN ('pendiente', 'error')
              AND identificador_externo IS NULL
              AND publicado_en IS NULL
            """,
            (
                ahora,
                ahora,
                publicacion_id,
                plataforma,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "No fue posible reservar el destino."
            )

        conexion.commit()

        return {
            **dict(fila),
            "estado_anterior": fila["estado"],
            "estado": "enviando",
            "intento_en": ahora,
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def confirmar_destino_educativo(
    publicacion_id: int,
    plataforma: str,
    identificador_externo: str,
    url_publicacion: str,
) -> dict:
    """
    Confirma una publicacion despues de obtener evidencia
    del envio real a la plataforma.

    No realiza envios externos.
    """

    from datetime import datetime, timezone
    from urllib.parse import urlparse

    if (
        not isinstance(publicacion_id, int)
        or isinstance(publicacion_id, bool)
        or publicacion_id <= 0
    ):
        raise ValueError("Identificador de publicacion invalido.")

    if not isinstance(plataforma, str):
        raise ValueError("Plataforma invalida.")

    plataforma = plataforma.strip().lower()

    if plataforma not in PLATAFORMAS:
        raise ValueError("Plataforma no autorizada.")

    if not isinstance(identificador_externo, str):
        raise ValueError("Identificador externo invalido.")

    identificador_externo = identificador_externo.strip()

    if not identificador_externo or len(identificador_externo) > 255:
        raise ValueError("Identificador externo invalido.")

    if not isinstance(url_publicacion, str):
        raise ValueError("URL de publicacion invalida.")

    url_publicacion = url_publicacion.strip()

    if not url_publicacion or len(url_publicacion) > 2000:
        raise ValueError("URL de publicacion invalida.")

    parsed = urlparse(url_publicacion)

    dominios = {
        "discord": {"discord.com", "www.discord.com"},
        "x": {"x.com", "www.x.com", "twitter.com", "www.twitter.com"},
        "linkedin": {"linkedin.com", "www.linkedin.com"},
    }

    if (
        parsed.scheme != "https"
        or parsed.hostname not in dominios[plataforma]
        or not parsed.path
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(
            "La URL no corresponde a la plataforma seleccionada."
        )

    ahora = datetime.now(timezone.utc).isoformat()

    conexion = sqlite3.connect(RUTA_BD, timeout=10)

    try:
        conexion.execute("BEGIN IMMEDIATE")

        cursor = conexion.execute(
            """
            UPDATE publicaciones_educativas_destinos
            SET estado = 'publicado',
                identificador_externo = ?,
                url_publicacion = ?,
                publicado_en = ?,
                actualizado_en = ?,
                error = NULL
            WHERE publicacion_id = ?
              AND plataforma = ?
              AND estado IN ('enviando', 'resultado_desconocido')
              AND identificador_externo IS NULL
              AND publicado_en IS NULL
            """,
            (
                identificador_externo,
                url_publicacion,
                ahora,
                ahora,
                publicacion_id,
                plataforma,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "No se puede confirmar este destino: "
                "no existe, no esta reservado o ya fue confirmado."
            )

        conexion.commit()

        return {
            "publicacion_id": publicacion_id,
            "plataforma": plataforma,
            "estado": "publicado",
            "identificador_externo": identificador_externo,
            "url_publicacion": url_publicacion,
            "publicado_en": ahora,
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def marcar_resultado_desconocido_educativo(
    publicacion_id: int,
    plataforma: str,
    detalle: str,
) -> bool:
    """
    Bloquea un destino cuando el resultado de un envio
    no pudo verificarse.

    Debe llamarse si el envio pudo haberse ejecutado.
    No realiza publicaciones externas.
    """

    from datetime import datetime, timezone

    if (
        not isinstance(publicacion_id, int)
        or isinstance(publicacion_id, bool)
        or publicacion_id <= 0
    ):
        raise ValueError("Identificador de publicacion invalido.")

    if not isinstance(plataforma, str):
        raise ValueError("Plataforma invalida.")

    plataforma = plataforma.strip().lower()

    if plataforma not in PLATAFORMAS:
        raise ValueError("Plataforma no autorizada.")

    if not isinstance(detalle, str) or not detalle.strip():
        raise ValueError("El detalle del incidente es obligatorio.")

    detalle = detalle.strip()[:500]
    ahora = datetime.now(timezone.utc).isoformat()

    conexion = sqlite3.connect(RUTA_BD, timeout=10)

    try:
        conexion.execute("BEGIN IMMEDIATE")

        cursor = conexion.execute(
            """
            UPDATE publicaciones_educativas_destinos
            SET estado = 'resultado_desconocido',
                error = ?,
                actualizado_en = ?
            WHERE publicacion_id = ?
              AND plataforma = ?
              AND estado = 'enviando'
              AND identificador_externo IS NULL
              AND publicado_en IS NULL
            """,
            (
                detalle,
                ahora,
                publicacion_id,
                plataforma,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "No se puede marcar el resultado como desconocido: "
                "el destino no existe o no esta en estado enviando."
            )

        conexion.commit()
        return True

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()