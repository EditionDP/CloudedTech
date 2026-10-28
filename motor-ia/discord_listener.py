"""Escucha de mensajes nuevos de Discord para CloudEdTech."""

import os
import asyncio
import logging

import discord
from dotenv import load_dotenv

from armar_json_bot_python import construir_paquete
from base_datos import crear_tabla
from discord_reacciones import crear_tabla_reacciones, reemplazar_reacciones_mensaje
from procesamiento import procesar_actividad

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("cloudedtech.discord")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logger.info("Bot conectado: %s", client.user)
    for guild in client.guilds:
        logger.info("Servidor: %s", guild.name)
        for channel in guild.text_channels:
            logger.info("Canal disponible: #%s (%s)", channel.name, channel.id)


@client.event

@client.event
async def on_message(message):
    if (
        message.guild is None
        or message.guild.id != SERVIDOR_DISCORD_AUTORIZADO
    ):
        return

    if not message.content.strip():
        return

    es_foro_educativo = message.channel.id == FORO_EDUCATIVO_HILO_ID
    es_webhook_simulador = (
        es_foro_educativo
        and message.webhook_id == 1562221227395915907
        and message.author.bot
        and "[Simulacion CloudEdTech]" in message.content
    )

    if message.author.bot and not es_webhook_simulador:
        return

    if es_foro_educativo:
        if os.getenv("FORO_IA_ACTIVO", "0") != "1":
            return

        from clasificador_foro_tecnologico import clasificar_consulta
        from respuestas_foro_ia import generar_respuesta_foro_ia
        from respuestas_foro_discord_db import (
            reservar_respuesta,
            confirmar_respuesta,
            marcar_error_respuesta,
            marcar_resultado_desconocido,
        )

        clasificacion = clasificar_consulta(message.content)

        if not clasificacion.get("es_consulta_tecnologica"):
            return

        try:
            reservado = await asyncio.to_thread(
                reservar_respuesta,
                message.id,
                message.channel.id,
                message.guild.id,
            )

            if not reservado:
                logger.info(
                    "Pregunta educativa ya registrada: %s",
                    message.id,
                )
                return

            try:
                resultado = await asyncio.to_thread(
                    generar_respuesta_foro_ia,
                    message.content,
                )
                respuesta = resultado.get("respuesta")

                if not respuesta:
                    await asyncio.to_thread(
                        marcar_error_respuesta,
                        message.id,
                        "Groq no genero respuesta educativa.",
                    )
                    return

            except Exception as error:
                await asyncio.to_thread(
                    marcar_error_respuesta,
                    message.id,
                    str(error),
                )
                logger.exception(
                    "Error generando respuesta educativa: %s",
                    message.id,
                )
                return

            try:
                enviado = await message.reply(
                    respuesta,
                    mention_author=False,
                )
            except Exception as error:
                await asyncio.to_thread(
                    marcar_resultado_desconocido,
                    message.id,
                    str(error),
                )
                logger.exception(
                    "Resultado incierto al enviar respuesta: %s",
                    message.id,
                )
                return

            await asyncio.to_thread(
                confirmar_respuesta,
                message.id,
                enviado.id,
                respuesta,
            )

            logger.info(
                "Respuesta educativa publicada: pregunta=%s respuesta=%s",
                message.id,
                enviado.id,
            )

        except Exception:
            logger.exception(
                "Error en flujo educativo: %s",
                message.id,
            )

        return

    if message.channel.id not in CANALES_PERMITIDOS_REACCIONES:
        return

    try:
        paquete = construir_paquete([message])

        if not paquete:
            return

        resultado = await asyncio.to_thread(
            procesar_actividad,
            paquete,
        )

        logger.info(
            "Mensaje %s en #%s: %s",
            message.id,
            message.channel.name,
            resultado,
        )

    except Exception:
        logger.exception(
            "Error procesando mensaje %s",
            message.id,
        )




CANALES_PERMITIDOS_REACCIONES = {
    1562138937089200242,
    1562219960451858443,
    1562220312177934346,
    1562220090437541958,
    1562219605248704592,
    1562220239129809097,
}


SERVIDOR_DISCORD_AUTORIZADO = 1562138935948353588
FORO_EDUCATIVO_HILO_ID = 1563254807479976018

_bloqueo_reacciones = asyncio.Lock()


async def sincronizar_reaccion(payload):
    """Sincroniza el estado completo del mensaje desde Discord."""
    if payload.guild_id != SERVIDOR_DISCORD_AUTORIZADO:
        return

    if payload.channel_id not in CANALES_PERMITIDOS_REACCIONES:
        return

    async with _bloqueo_reacciones:
        try:
            canal = client.get_channel(payload.channel_id)

            if canal is None:
                canal = await client.fetch_channel(payload.channel_id)

            mensaje = await canal.fetch_message(payload.message_id)

            reacciones = [
                {
                    "emoji": str(reaccion.emoji),
                    "cantidad": reaccion.count,
                }
                for reaccion in mensaje.reactions
            ]

            await asyncio.to_thread(
                reemplazar_reacciones_mensaje,
                payload.guild_id,
                payload.channel_id,
                payload.message_id,
                reacciones,
            )

            logger.info(
                "Reacciones sincronizadas: mensaje=%s emojis=%s",
                payload.message_id,
                len(reacciones),
            )

        except discord.NotFound:
            logger.warning(
                "Mensaje no disponible para sincronizar: %s",
                payload.message_id,
            )
        except Exception:
            logger.exception(
                "Error sincronizando reacciones del mensaje %s",
                payload.message_id,
            )


@client.event
async def on_raw_reaction_add(payload):
    await sincronizar_reaccion(payload)


@client.event
async def on_raw_reaction_remove(payload):
    await sincronizar_reaccion(payload)



def main():
    token = os.getenv("DISCORD_BOT_TOKEN") or os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError(
            "Falta DISCORD_BOT_TOKEN o DISCORD_TOKEN en el entorno."
        )

    crear_tabla()
    crear_tabla_reacciones()
    client.run(token)


if __name__ == "__main__":
    main()