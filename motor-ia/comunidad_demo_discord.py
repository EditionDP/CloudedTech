"""Publicador controlado para pruebas de comunidad simulada.

No publica automaticamente.
No modifica la base de datos.
"""

import asyncio
import os

import discord
from dotenv import load_dotenv


SERVIDOR_AUTORIZADO = 1562138935948353588

# PASO 3207: DESTINOS CENTRALIZADOS
from comunidad_demo_publicacion_config import DESTINOS

CANALES_AUTORIZADOS = {
    nombre: int(identificador)
    for nombre, identificador in DESTINOS.items()
}


PREFIJO_SIMULACION = "[SIMULACION CLOUDEDTECH]"


def preparar_publicacion(mensaje):
    """Valida y prepara un mensaje sin enviarlo."""

    if not isinstance(mensaje, dict):
        raise ValueError("Mensaje invalido")

    if mensaje.get("es_simulado") is not True:
        raise ValueError("Solo se admiten mensajes simulados")

    if mensaje.get("origen") != "discord_demo":
        raise ValueError("Origen no autorizado")

    if mensaje.get("publicar_discord") is not True:
        raise ValueError("Publicacion Discord no autorizada")

    canal = mensaje.get("canal")

    if canal not in CANALES_AUTORIZADOS:
        raise ValueError("Canal no autorizado")

    autor = str(mensaje.get("autor", "")).strip()
    texto = str(mensaje.get("texto", "")).strip()

    if not autor or not texto:
        raise ValueError("Autor o contenido vacio")

    contenido = (
        f"{PREFIJO_SIMULACION}\n"
        f"Participante virtual: {autor}\n"
        f"{texto}"
    )

    if len(contenido) > 2000:
        raise ValueError("Mensaje supera el limite de Discord")

    return {
        "guild_id": SERVIDOR_AUTORIZADO,
        "canal": canal,
        "canal_id": CANALES_AUTORIZADOS[canal],
        "contenido": contenido,
        "id_simulacion": mensaje.get("id_simulacion"),
    }


async def _enviar_preparado(publicacion):
    """Realiza un unico intento de envio autorizado."""

    load_dotenv(
        os.path.join(os.path.dirname(__file__), ".env")
    )

    token = (
        os.getenv("DISCORD_BOT_TOKEN")
        or os.getenv("DISCORD_TOKEN")
    )

    if not token:
        raise RuntimeError("Token Discord no configurado")

    intents = discord.Intents.default()
    cliente = discord.Client(intents=intents)

    resultado = {}
    envio_iniciado = False

    @cliente.event
    async def on_ready():
        nonlocal envio_iniciado

        try:
            servidor = cliente.get_guild(
                SERVIDOR_AUTORIZADO
            )

            if servidor is None:
                raise RuntimeError(
                    "Servidor Discord no autorizado o inaccesible"
                )

            canal = servidor.get_channel_or_thread(
                publicacion["canal_id"]
            )

            if canal is None:
                canal = await cliente.fetch_channel(
                    publicacion["canal_id"]
                )

            if not isinstance(
                canal,
                (discord.TextChannel, discord.Thread),
            ):
                raise RuntimeError(
                    "Destino no es canal de texto ni hilo"
                )

            if canal.guild.id != SERVIDOR_AUTORIZADO:
                raise PermissionError(
                    "Destino fuera del servidor autorizado"
                )

            miembro = servidor.me

            if miembro is None:
                raise RuntimeError(
                    "No se pudo verificar el bot"
                )

            permisos = canal.permissions_for(miembro)

            if not permisos.view_channel:
                raise PermissionError(
                    "El bot no puede visualizar el destino"
                )

            if isinstance(canal, discord.Thread):
                if canal.archived or canal.locked:
                    raise RuntimeError(
                        "El hilo educativo esta archivado o bloqueado"
                    )

                if not permisos.send_messages_in_threads:
                    raise PermissionError(
                        "El bot no puede publicar en hilos"
                    )
            elif not permisos.send_messages:
                raise PermissionError(
                    "El bot no puede publicar en el canal"
                )

            envio_iniciado = True

            enviado = await canal.send(
                publicacion["contenido"],
                allowed_mentions=discord.AllowedMentions.none(),
            )

            resultado.update({
                "estado": "publicado",
                "guild_id": str(servidor.id),
                "channel_id": str(canal.id),
                "message_id": str(enviado.id),
            })

        except Exception as error:
            resultado["estado"] = (
                "resultado_desconocido"
                if envio_iniciado
                else "no_enviado"
            )
            resultado["error"] = str(error)

        finally:
            await cliente.close()

    try:
        await asyncio.wait_for(
            cliente.start(token, reconnect=False),
            timeout=60,
        )
    except Exception as error:
        if resultado.get("estado") != "publicado":
            resultado["estado"] = (
                "resultado_desconocido"
                if envio_iniciado
                else "no_enviado"
            )
            resultado["error"] = str(error)

    return resultado


def publicar_mensaje_simulado(
    mensaje,
    *,
    confirmar_envio=False,
):
    """Publica solo si existe autorizacion explicita."""

    publicacion = preparar_publicacion(mensaje)

    if confirmar_envio is not True:
        return {
            "estado": "vista_previa",
            "publicacion": publicacion,
        }

    return asyncio.run(
        _enviar_preparado(publicacion)
    )
