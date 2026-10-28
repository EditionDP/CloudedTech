from base_datos import guardar_analisis, listar_interacciones
from base_datos import actualizar_clasificacion_queja
from clasificador_quejas import clasificar_queja
from cerebro_ia import cadena


def analizar_pendientes(limite: int = 20) -> dict:
    """Analiza mensajes pendientes sin bloquear la cola ante errores."""
    import logging
    import sqlite3
    from base_datos import RUTA_BD

    logger = logging.getLogger(__name__)

    if not isinstance(limite, int) or not 1 <= limite <= 100:
        raise ValueError("El limite debe estar entre 1 y 100.")

    # Los fallos se omiten solo durante el ciclo actual.
    # En el siguiente ciclo se pueden reintentar.
    fallidos = set()

    with sqlite3.connect(RUTA_BD, timeout=30) as conexion:
        conexion.row_factory = sqlite3.Row
        mensajes = [
            dict(fila)
            for fila in conexion.execute(
                """
                SELECT id, texto, canal
                FROM interacciones
                WHERE estado = 'pendiente'
                ORDER BY id ASC
                """
            ).fetchall()
            if fila["id"] not in fallidos
        ][:limite]

    analizados = 0
    errores = 0

    for mensaje in mensajes:
        try:
            respuesta = cadena.invoke({
                "texto": mensaje["texto"],
                "canal": mensaje["canal"],
            })

            kpis = respuesta.model_dump()

            guardado = guardar_analisis(
                mensaje["id"],
                kpis["relevancia"],
                kpis["sentimiento"],
                kpis["sentiment_score"],
                kpis["temas_clave"],
                kpis["tema"],
                kpis["segmento"],
                kpis["razonamiento"],
            )

            if guardado:
                clasificacion_queja = clasificar_queja(
                    mensaje["texto"],
                    canal=mensaje["canal"],
                )
                actualizar_clasificacion_queja(
                    mensaje["id"],
                    clasificacion_queja["es_queja"],
                )
                analizados += 1
            else:
                errores += 1
                fallidos.add(mensaje["id"])

        except Exception:
            errores += 1
            fallidos.add(mensaje["id"])
            logger.exception(
                "Error analizando mensaje ID=%s",
                mensaje["id"],
            )

    return {
        "status": "exito",
        "procesados": len(mensajes),
        "analizados": analizados,
        "errores": errores,
    }


def reanalizar_interacciones(ids: list[int]) -> dict:
    import sqlite3
    from base_datos import RUTA_BD

    ids_validos = list(dict.fromkeys(
        identificador
        for identificador in ids
        if type(identificador) is int and identificador > 0
    ))

    if not ids_validos:
        return {
            "status": "exito",
            "solicitados": len(ids),
            "encontrados": 0,
            "analizados": 0,
            "errores": 0,
        }

    seleccionados = []

    with sqlite3.connect(RUTA_BD, timeout=15) as conexion:
        conexion.row_factory = sqlite3.Row

        for identificador in ids_validos:
            fila = conexion.execute(
                """
                SELECT id, texto, canal
                FROM interacciones
                WHERE id = ?
                """,
                (identificador,),
            ).fetchone()

            if fila is not None:
                seleccionados.append(dict(fila))

    analizados = 0
    errores = 0

    for mensaje in seleccionados:
        try:
            respuesta = cadena.invoke({
                "texto": mensaje["texto"],
                "canal": mensaje["canal"]
            })

            kpis = respuesta.model_dump()

            guardado = guardar_analisis(
                mensaje["id"],
                kpis["relevancia"],
                kpis["sentimiento"],
                kpis["sentiment_score"],
                kpis["temas_clave"],
                kpis["tema"],
                kpis["segmento"],
                kpis["razonamiento"],
            )

            if guardado:
                clasificacion_queja = clasificar_queja(
                    mensaje["texto"],
                    canal=mensaje["canal"],
                )
                actualizar_clasificacion_queja(
                    mensaje["id"],
                    clasificacion_queja["es_queja"],
                )
                analizados += 1
            else:
                errores += 1

        except Exception:
            errores += 1

    return {
        "status": "exito",
        "solicitados": len(ids),
        "encontrados": len(seleccionados),
        "analizados": analizados,
        "errores": errores,
    }


def preparar_copywriting_desde_analisis(
    ids_locales: list[int],
    *,
    permitir_conexion: bool = False,
) -> dict:
    """Prepara registros Copywriting sin escribir datos remotos."""
    from adaptador_copywriting import preparar_resultado_copywriting

    preparados = []
    errores = []

    for id_local in ids_locales:
        try:
            registro = preparar_resultado_copywriting(
                id_local,
                permitir_conexion=permitir_conexion,
            )
            preparados.append(registro)
        except Exception as exc:
            errores.append({
                "id_local": id_local,
                "error": str(exc),
            })

    return {
        "preparados": preparados,
        "errores": errores,
        "total_preparados": len(preparados),
        "total_errores": len(errores),
    }
