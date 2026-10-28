"""Historial persistente de consultas de la comunidad demo.

No crea conexiones automaticamente.
No publica en Discord.
"""

import hashlib
import sqlite3
import unicodedata


def normalizar_pregunta(texto):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Pregunta invalida")

    normalizado = unicodedata.normalize("NFKC", texto)
    return " ".join(normalizado.casefold().split())


def calcular_clave_pregunta(texto):
    normalizado = normalizar_pregunta(texto)
    return hashlib.sha256(
        normalizado.encode("utf-8")
    ).hexdigest()


def crear_tabla_historial(conexion):
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS comunidad_demo_historial (
            clave_pregunta TEXT PRIMARY KEY,
            pregunta TEXT NOT NULL,
            tema TEXT NOT NULL,
            autor TEXT NOT NULL,
            id_simulacion TEXT NOT NULL UNIQUE,
            creado_en TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def registrar_pregunta(conexion, mensaje):
    if not isinstance(mensaje, dict):
        raise ValueError("Mensaje invalido")

    if mensaje.get("es_simulado") is not True:
        raise ValueError("Solo se admiten mensajes simulados")

    if mensaje.get("origen") != "discord_demo":
        raise ValueError("Origen no autorizado")

    pregunta = mensaje.get("texto")
    clave = calcular_clave_pregunta(pregunta)

    tema = mensaje.get("tema")
    autor = mensaje.get("autor")
    identificador = mensaje.get("id_simulacion")

    if not all(
        isinstance(valor, str) and valor.strip()
        for valor in (tema, autor, identificador)
    ):
        raise ValueError("Metadatos incompletos")

    cursor = conexion.execute(
        """
        INSERT OR IGNORE INTO comunidad_demo_historial (
            clave_pregunta,
            pregunta,
            tema,
            autor,
            id_simulacion
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (clave, pregunta, tema, autor, identificador),
    )

    return cursor.rowcount == 1


def cargar_preguntas_utilizadas(conexion):
    filas = conexion.execute(
        """
        SELECT pregunta
        FROM comunidad_demo_historial
        """
    ).fetchall()

    return {
        normalizar_pregunta(fila[0])
        for fila in filas
    }


def contar_preguntas(conexion):
    fila = conexion.execute(
        "SELECT COUNT(*) FROM comunidad_demo_historial"
    ).fetchone()

    return int(fila[0])
