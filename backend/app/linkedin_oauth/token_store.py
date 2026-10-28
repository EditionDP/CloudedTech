"""Almacenamiento cifrado de tokens OAuth de LinkedIn."""

import os
import sqlite3
import time
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BACKEND_DIR / "linkedin_oauth_tokens.db"

load_dotenv(BACKEND_DIR / ".env")


def _fernet() -> Fernet:
    clave = os.getenv("LINKEDIN_TOKEN_ENCRYPTION_KEY", "").strip()

    if not clave:
        raise RuntimeError(
            "No esta configurada la clave de cifrado de LinkedIn."
        )

    return Fernet(clave.encode("ascii"))


def _conexion():
    conexion = sqlite3.connect(DATABASE_PATH, timeout=10)
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS linkedin_tokens (
            user_id INTEGER PRIMARY KEY,
            access_token_encrypted BLOB NOT NULL,
            expires_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
        """
    )
    return conexion


def guardar_token(
    user_id: int,
    access_token: str,
    expires_in: int,
) -> None:
    if user_id <= 0 or not access_token or expires_in <= 0:
        raise ValueError("Datos de token invalidos.")

    token_cifrado = _fernet().encrypt(
        access_token.encode("utf-8")
    )

    ahora = int(time.time())
    expiracion = ahora + expires_in

    with _conexion() as conexion:
        conexion.execute(
            """
            INSERT INTO linkedin_tokens (
                user_id,
                access_token_encrypted,
                expires_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                access_token_encrypted=excluded.access_token_encrypted,
                expires_at=excluded.expires_at,
                updated_at=excluded.updated_at
            """,
            (user_id, token_cifrado, expiracion, ahora),
        )


def obtener_token(user_id: int) -> str | None:
    if user_id <= 0:
        return None

    with _conexion() as conexion:
        fila = conexion.execute(
            """
            SELECT access_token_encrypted, expires_at
            FROM linkedin_tokens
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if fila is None or fila[1] <= int(time.time()):
        return None

    return _fernet().decrypt(fila[0]).decode("utf-8")


def eliminar_token(user_id: int) -> None:
    with _conexion() as conexion:
        conexion.execute(
            "DELETE FROM linkedin_tokens WHERE user_id = ?",
            (user_id,),
        )
