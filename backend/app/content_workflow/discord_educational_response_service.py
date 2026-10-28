"""Registro seguro de borradores educativos para Discord.

No publica mensajes ni inicia conexiones con Discord.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.content_workflow.discord_educational_response_model import (
    DiscordEducationalResponse,
)


def registrar_borrador_educativo(
    db: Session,
    *,
    identidad: dict,
    pregunta_original: str,
    respuesta: str,
    tema: str | None = None,
) -> tuple[DiscordEducationalResponse | None, bool]:
    """Registra un borrador; devuelve (registro, creado).

    Si ya existe la identidad, no modifica el registro anterior.
    """

    pregunta = pregunta_original.strip()
    borrador = respuesta.strip()

    if not pregunta:
        raise ValueError("La pregunta original no puede estar vacia")

    if not borrador:
        raise ValueError("La respuesta educativa no puede estar vacia")

    if len(borrador) > 2000:
        raise ValueError("La respuesta supera el limite de Discord")

    if tema is not None and len(tema) > 100:
        raise ValueError("El tema supera 100 caracteres")

    campos = (
        "clave_unica",
        "guild_id",
        "channel_id",
        "source_message_id",
    )

    if any(not identidad.get(campo) for campo in campos):
        raise ValueError("Identidad de Discord incompleta")

    registro = DiscordEducationalResponse(
        clave_unica=identidad["clave_unica"],
        guild_id=identidad["guild_id"],
        channel_id=identidad["channel_id"],
        source_message_id=identidad["source_message_id"],
        pregunta_original=pregunta,
        respuesta=borrador,
        tema=tema,
        estado="borrador",
    )

    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)
    except IntegrityError:
        db.rollback()
        existente = (
            db.query(DiscordEducationalResponse)
            .filter_by(clave_unica=identidad["clave_unica"])
            .first()
        )

        if existente is None:
            raise

        return existente, False

    return registro, True
