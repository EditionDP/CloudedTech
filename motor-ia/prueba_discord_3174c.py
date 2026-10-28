import asyncio
import inspect
import json
from pathlib import Path

from comunidad_demo_webhook_publicador import publicar_webhook

print("=== PASO 3174-C: PUBLICACION REAL DISCORD ===")

config = json.loads(
    Path("comunidad_demo_webhooks.json").read_text(encoding="utf-8")
)

# Buscar el ID del servidor en la configuracion sin imprimir secretos.
def contiene_servidor(obj):
    if isinstance(obj, dict):
        return any(
            contiene_servidor(v)
            for v in obj.values()
        )
    if isinstance(obj, list):
        return any(contiene_servidor(v) for v in obj)
    return str(obj) == "1562138935948353588"

if not contiene_servidor(config):
    print("AVISO: ID del servidor no encontrado en la configuracion.")
    print("No se enviara el mensaje hasta revisar el destino.")
    raise SystemExit(1)

mensaje = {
    "id_simulacion": "prueba_cloudedtech_3174c",
    "autor": "CloudEdTech Demo",
    "canal": "general",
    "texto": (
        "CloudEdTech | Primera prueba real\n\n"
        "Hola, comunidad de CloudEDTech_OF. "
        "Estamos verificando la integracion de CloudEdTech "
        "con Discord mediante webhook.\n\n"
        "Esta es una publicacion tecnica de prueba."
    ),
    "origen": "discord_demo",
    "es_simulado": True,
    "publicar_discord": True,
}

resultado = publicar_webhook(mensaje, confirmar=True)

if inspect.isawaitable(resultado):
    resultado = asyncio.run(resultado)

print("RESULTADO:")

if isinstance(resultado, dict):
    for clave, valor in resultado.items():
        if any(
            palabra in clave.lower()
            for palabra in ("url", "token", "secret", "webhook")
        ):
            print(clave, "[OCULTO]")
        else:
            print(clave, valor)
else:
    print("TIPO:", type(resultado).__name__)

print("PASO_3174_C_FINALIZADO")
