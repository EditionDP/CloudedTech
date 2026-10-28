import asyncio
import os
import urllib.error
import urllib.request
import json
from datetime import datetime, timezone

from app.discord_connector.schemas import DiscordMessage


MOTOR_IA_URL = os.getenv(
    "MOTOR_IA_URL",
    "http://127.0.0.1:8003",
).rstrip("/")


def _enviar_a_motor_ia(paquete: dict) -> dict:
    token = os.getenv("MOTOR_INTERNAL_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            "No esta configurado MOTOR_INTERNAL_TOKEN."
        )

    solicitud = urllib.request.Request(
        MOTOR_IA_URL + "/api/community/discord/ingest",
        data=json.dumps(paquete).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Internal-Token": token,
        },
        method="POST",
    )

    with urllib.request.urlopen(solicitud, timeout=15) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


async def ingest_discord_message(
    message: DiscordMessage,
) -> None:
    """Envia mensajes Discord al Motor IA con deduplicacion."""

    fecha = message.created_at

    if isinstance(fecha, datetime):
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        fecha = fecha.astimezone(timezone.utc).isoformat()
    else:
        fecha = str(fecha)

    paquete = {
        "origen_comunidad": "discord",
        "periodo_referencia": "Discord_Tiempo_Real",
        "interacciones": [
            {
                "autor": message.author_name,
                "canal": message.channel_name,
                "texto": message.content,
                "guild_id": message.guild_id,
                "guild_name": message.guild_name,
                "channel_id": message.channel_id,
                "message_id": message.message_id,
                "author_id": message.author_id,
                "enviado_en": fecha,
            }
        ],
    }

    try:
        resultado = await asyncio.to_thread(
            _enviar_a_motor_ia,
            paquete,
        )

        if resultado.get("status") != "exito":
            raise RuntimeError(
                "El Motor IA no confirmo la ingesta."
            )

        print(
            "[INGESTA DISCORD] "
            f"nuevos={resultado.get('guardadas_nuevas', 0)} "
            f"repetidos={resultado.get('repetidas_omitidas', 0)}"
        )
        # Preparacion educativa posterior a la ingesta confirmada.
        # No publica respuestas en Discord.
        if (
            type(resultado.get("guardadas_nuevas")) is int
            and resultado["guardadas_nuevas"] == 1
        ):
            try:
                from app.content_workflow.discord_educational_bridge import (
                    cargar_dependencias_educativas,
                )
                from app.content_workflow.discord_educational_coordinator import (
                    coordinar_borrador_educativo,
                )
                from app.database.session import SessionLocal

                dependencias = cargar_dependencias_educativas()

                # No abrir sesion SQL si el canal no esta autorizado.
                if dependencias["canal_autorizado"](message.channel_id):
                    db = SessionLocal()

                    try:
                        educativo = await asyncio.to_thread(
                            coordinar_borrador_educativo,
                            db,
                            guild_id=message.guild_id,
                            channel_id=message.channel_id,
                            message_id=message.message_id,
                            texto=message.content,
                            preparar=dependencias["preparar"],
                            crear_identidad=dependencias["crear_identidad"],
                            canal_autorizado=dependencias["canal_autorizado"],
                        )

                        print(
                            "[FORO EDUCATIVO] "
                            f"estado={educativo.get('estado')} "
                            f"creado={educativo.get('creado', False)}"
                        )
                    finally:
                        db.close()

            except Exception as error_educativo:
                # Un error educativo no invalida la ingesta confirmada.
                print(
                    "[FORO EDUCATIVO] Error aislado:",
                    type(error_educativo).__name__,
                )


    except urllib.error.HTTPError as error:
        print(
            "[INGESTA DISCORD] Error HTTP:",
            error.code,
        )
        raise

    except Exception as error:
        print(
            "[INGESTA DISCORD] Error:",
            type(error).__name__,
        )
        raise
