"""Pipeline de comunidad simulada, sin publicacion externa.

La funcion preparar_mensaje no escribe en la base principal.
La funcion registrar_en_motor requiere autorizacion explicita.
"""

from comunidad_demo_adaptador import construir_actividad_simulada


def preparar_mensaje(mensaje):
    """Convierte un mensaje simulado al esquema del Motor IA."""
    if not isinstance(mensaje, dict):
        raise ValueError("Mensaje simulado invalido")

    if mensaje.get("origen") != "discord_demo":
        raise ValueError("Origen de simulacion no autorizado")

    if mensaje.get("es_simulado") is not True:
        raise ValueError("El mensaje debe ser simulado")

    if mensaje.get("publicar_discord") is not False:
        raise ValueError("Publicacion en Discord prohibida")

    resultado = construir_actividad_simulada(mensaje)

    if resultado.get("origen_comunidad") != "discord_demo":
        raise ValueError("Origen del adaptador invalido")

    if resultado.get("publicar_discord") is not False:
        raise ValueError("Publicacion del adaptador no autorizada")

    actividad = resultado["actividad"]

    if actividad.get("origen_comunidad") != "discord_demo":
        raise ValueError("Origen de actividad invalido")

    return actividad


def registrar_en_motor(mensaje, *, permitir_escritura=False):
    """Registra mediante el procesamiento existente, solo si se autoriza."""
    if permitir_escritura is not True:
        raise PermissionError(
            "Escritura deshabilitada hasta habilitar el generador"
        )

    actividad = preparar_mensaje(mensaje)

    from procesamiento import procesar_actividad

    resultado = procesar_actividad(actividad)

    if resultado.get("status") != "exito":
        raise RuntimeError("El Motor IA rechazo la actividad")

    return resultado
