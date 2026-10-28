"""Estados temporales OAuth de LinkedIn para desarrollo local."""

import secrets
import threading
import time
from dataclasses import dataclass


STATE_TTL_SECONDS = 600


@dataclass(frozen=True)
class OAuthState:
    user_id: int
    expires_at: float


_estados: dict[str, OAuthState] = {}
_lock = threading.Lock()


def crear_state(user_id: int) -> str:
    if user_id <= 0:
        raise ValueError("Usuario invalido.")

    ahora = time.monotonic()
    state = secrets.token_urlsafe(32)

    with _lock:
        _limpiar_expirados(ahora)
        _estados[state] = OAuthState(
            user_id=user_id,
            expires_at=ahora + STATE_TTL_SECONDS,
        )

    return state


def consumir_state(state: str, user_id: int) -> bool:
    if not state or user_id <= 0:
        return False

    ahora = time.monotonic()

    with _lock:
        # Retirar primero el estado para impedir su reutilizacion.
        registro = _estados.pop(state, None)
        _limpiar_expirados(ahora)

        if registro is None:
            return False

        if registro.expires_at <= ahora:
            return False

        return secrets.compare_digest(
            str(registro.user_id),
            str(user_id),
        )


def _limpiar_expirados(ahora: float) -> None:
    expirados = [
        clave
        for clave, registro in _estados.items()
        if registro.expires_at <= ahora
    ]

    for clave in expirados:
        _estados.pop(clave, None)
