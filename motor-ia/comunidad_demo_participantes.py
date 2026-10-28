"""Catalogo persistente de participantes virtuales CloudEdTech."""

import json
import threading
import uuid
from pathlib import Path

from comunidad_demo_usuarios import PARTICIPANTES_DEMO


ARCHIVO = Path(__file__).parent / "comunidad_demo_participantes.json"
BLOQUEO = threading.RLock()


def _guardar(registros):
    temporal = ARCHIVO.with_suffix(".tmp")
    temporal.write_text(
        json.dumps(registros, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporal.replace(ARCHIVO)


def _leer():
    if not ARCHIVO.exists():
        iniciales = [
            {
                "id": f"demo_user_{indice:03d}",
                "nombre": nombre,
                "activo": True,
                "avatar_url": None,
                "eliminado": False,
                "es_simulado": True,
            }
            for indice, nombre in enumerate(
                PARTICIPANTES_DEMO, start=1
            )
        ]
        _guardar(iniciales)

    datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))

    if not isinstance(datos, list):
        raise ValueError("Catalogo de participantes invalido")

    return datos


def listar_participantes(incluir_eliminados=False):
    with BLOQUEO:
        registros = _leer()

        if incluir_eliminados:
            return registros

        return [
            dict(usuario)
            for usuario in registros
            if not usuario.get("eliminado", False)
        ]


def participantes_activos():
    return [
        usuario
        for usuario in listar_participantes()
        if usuario.get("activo") is True
    ]


def crear_participante(nombre, avatar_url=None):
    nombre = str(nombre).strip()

    if not 2 <= len(nombre) <= 80:
        raise ValueError("Nombre entre 2 y 80 caracteres")

    with BLOQUEO:
        registros = _leer()

        if any(
            u["nombre"].casefold() == nombre.casefold()
            and not u.get("eliminado", False)
            for u in registros
        ):
            raise ValueError("Ya existe ese participante")

        nuevo = {
            "id": "demo_user_" + uuid.uuid4().hex,
            "nombre": nombre,
            "activo": True,
            "avatar_url": avatar_url,
            "eliminado": False,
            "es_simulado": True,
        }

        registros.append(nuevo)
        _guardar(registros)

        return dict(nuevo)


def actualizar_participante(
    identificador,
    *,
    nombre=None,
    activo=None,
    avatar_url=None,
):
    with BLOQUEO:
        registros = _leer()

        usuario = next(
            (
                u for u in registros
                if u["id"] == identificador
                and not u.get("eliminado", False)
            ),
            None,
        )

        if usuario is None:
            raise ValueError("Participante no encontrado")

        if nombre is not None:
            nombre = str(nombre).strip()

            if not 2 <= len(nombre) <= 80:
                raise ValueError("Nombre invalido")

            if any(
                u["id"] != identificador
                and u["nombre"].casefold() == nombre.casefold()
                and not u.get("eliminado", False)
                for u in registros
            ):
                raise ValueError("Nombre duplicado")

            usuario["nombre"] = nombre

        if activo is not None:
            if not isinstance(activo, bool):
                raise ValueError("Activo debe ser booleano")

            usuario["activo"] = activo

        if avatar_url is not None:
            usuario["avatar_url"] = avatar_url

        _guardar(registros)

        return dict(usuario)


def eliminar_participante(identificador):
    with BLOQUEO:
        registros = _leer()

        usuario = next(
            (
                u for u in registros
                if u["id"] == identificador
                and not u.get("eliminado", False)
            ),
            None,
        )

        if usuario is None:
            raise ValueError("Participante no encontrado")

        usuario["eliminado"] = True
        usuario["activo"] = False

        _guardar(registros)

        return {
            "id": identificador,
            "eliminado": True,
        }
