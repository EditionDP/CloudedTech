"""Publicador Discord para participantes virtuales CloudEdTech."""

import asyncio
import json
from pathlib import Path

import discord


ARCHIVO_CONFIG = (
    Path(__file__).parent / "comunidad_demo_webhooks.json"
)

ETIQUETA = "[Simulacion CloudEdTech]"


def preparar_mensaje_webhook(mensaje):
    if mensaje.get("origen") != "discord_demo":
        raise ValueError("Origen no autorizado")

    if mensaje.get("es_simulado") is not True:
        raise ValueError("Mensaje no simulado")

    config = json.loads(
        ARCHIVO_CONFIG.read_text(encoding="utf-8")
    )

    canal = mensaje.get("canal")
    destino = config["webhooks"].get(canal)

    if not destino:
        raise ValueError("Canal no autorizado")

    autor = str(mensaje.get("autor", "")).strip()
    texto = str(mensaje.get("texto", "")).strip()

    if not autor or not texto:
        raise ValueError("Mensaje incompleto")

    contenido = f"{texto}\n\n{ETIQUETA}"

    if len(contenido) > 2000:
        raise ValueError("Mensaje demasiado largo")

    return {
        "nombre": autor[:80],
        "contenido": contenido,
        "canal": canal,
        "channel_id": destino["channel_id"],
        "thread_id": destino.get("thread_id"),
        "webhook_url": destino["webhook_url"],
        "id_simulacion": mensaje.get("id_simulacion"),
    }


async def _publicar(preparado):
    import aiohttp

    envio_iniciado = False

    async with aiohttp.ClientSession() as sesion:
        fase_error = 'preparacion_webhook'
        try:
            webhook = discord.Webhook.from_url(
                preparado['webhook_url'],
                session=sesion,
            )
        except Exception as error:
            return {
                'estado': 'no_enviado',
                'fase_error': fase_error,
                'tipo_error': type(error).__name__,
                'id_simulacion': preparado['id_simulacion'],
            }

        try:
            envio_iniciado = True

            opciones_envio = {
                "content": preparado["contenido"],
                "username": preparado["nombre"],
                "wait": True,
                "allowed_mentions": discord.AllowedMentions.none(),
            }

            if preparado.get("thread_id"):
                opciones_envio["thread"] = discord.Object(
                    id=int(preparado["thread_id"])
                )

            enviado = await webhook.send(**opciones_envio)

            message_id = str(enviado.id)
            
            channel_id = str(preparado["channel_id"])
            
            try:
                canal_respuesta = getattr(enviado, "channel", None)
                canal_real = getattr(canal_respuesta, "id", None)
            except (AttributeError, TypeError):
                canal_real = None
            
            if canal_real is not None:
                channel_id = str(canal_real)
            
            if channel_id != str(preparado["channel_id"]):
                return {
                    "estado": "publicado_destino_no_coincide",
                    "channel_id": channel_id,
                    "message_id": message_id,
                    "thread_id": preparado.get("thread_id"),
                    "id_simulacion": preparado["id_simulacion"],
                }
            
            return {
                "estado": "publicado",
                "channel_id": channel_id,
                "message_id": message_id,
                "thread_id": preparado.get("thread_id"),
                "id_simulacion": preparado["id_simulacion"],
            }

        except discord.HTTPException as error:
            return {
                "estado": "rechazado_http",
                "http_status": getattr(error, "status", None),
                "discord_code": getattr(error, "code", None),
                "tipo_error": type(error).__name__,
                "id_simulacion": preparado["id_simulacion"],
            }
        
        except Exception as error:
            import traceback

            cuadros = traceback.extract_tb(error.__traceback__)
            ultimo = cuadros[-1] if cuadros else None

            return {
                "estado": (
                    "resultado_desconocido"
                    if envio_iniciado
                    else "no_enviado"
                ),
                "tipo_error": type(error).__name__,
                "modulo_error": (
                    Path(ultimo.filename).name if ultimo else None
                ),
                "funcion_error": ultimo.name if ultimo else None,
                "linea_error": ultimo.lineno if ultimo else None,
                "id_simulacion": preparado["id_simulacion"],
            }



def publicar_webhook(mensaje, *, confirmar=False):
    preparado = preparar_mensaje_webhook(mensaje)

    if confirmar is not True:
        return {
            "estado": "vista_previa",
            "canal": preparado["canal"],
            "nombre": preparado["nombre"],
            "contenido": preparado["contenido"],
        }

    return asyncio.run(_publicar(preparado))
