from datetime import datetime, timedelta

from base_datos import listar_interacciones, contar_contenidos
from metricas_foro import calcular_interacciones_foro
from periodos import ZONA_PROYECTO
import re



ORIGEN_PRUEBA = "TEST_INTEGRACION_MERGE"


def obtener_interacciones_reales(
    desde_utc=None,
    hasta_utc=None,
) -> list[dict]:
    """
    Obtiene las interacciones reales de Discord y excluye
    registros creados únicamente para pruebas de integración.
    """

    interacciones = listar_interacciones(
        limite=None,
        desde_utc=desde_utc,
        hasta_utc=hasta_utc,
    )

    return [
        item
        for item in interacciones
        if item.get("origen_comunidad") != ORIGEN_PRUEBA
        and item.get("origen_comunidad") != "discord_demo"
        and not str(item.get("autor") or "").strip().lower().startswith(
            ("cloudedtech community bot", "cloudedtech_oficial")
        )
    ]

def obtener_ventanas_comparables() -> dict:
    interacciones = obtener_interacciones_reales()

    if not interacciones:
        return {}

    ultimo_dato_utc = datetime.fromisoformat(
        interacciones[0]["enviado_en"]
    )

    ultimo_dato_local = ultimo_dato_utc.astimezone(ZONA_PROYECTO)

    inicio_semana_local = ultimo_dato_local - timedelta(
        days=ultimo_dato_local.weekday(),
        hours=ultimo_dato_local.hour,
        minutes=ultimo_dato_local.minute,
        seconds=ultimo_dato_local.second,
        microseconds=ultimo_dato_local.microsecond,
    )

    duracion = ultimo_dato_local - inicio_semana_local

    inicio_anterior_local = inicio_semana_local - timedelta(days=7)
    fin_anterior_local = inicio_anterior_local + duracion

    return {
        "actual_desde": inicio_semana_local,
        "actual_hasta": ultimo_dato_local,
        "anterior_desde": inicio_anterior_local,
        "anterior_hasta": fin_anterior_local,
    }

def calcular_comparacion_mensajes() -> dict:
    ventanas = obtener_ventanas_comparables()

    if not ventanas:
        return {
            "actual": 0,
            "anterior": 0,
            "cambio_porcentual": 0.0,
        }

    actuales = obtener_interacciones_reales(
        desde_utc=ventanas["actual_desde"],
        hasta_utc=ventanas["actual_hasta"] + timedelta(seconds=1),
    )

    anteriores = obtener_interacciones_reales(
        desde_utc=ventanas["anterior_desde"],
        hasta_utc=ventanas["anterior_hasta"] + timedelta(seconds=1),
    )

    total_actual = len(actuales)
    total_anterior = len(anteriores)

    if total_anterior == 0:
        cambio = None
    else:
        cambio = round(
            ((total_actual - total_anterior) / total_anterior) * 100,
            1,
        )

    

    return {
        "actual": total_actual,
        "anterior": total_anterior,
        "cambio_porcentual": cambio,
    }

def calcular_comparacion_sentimiento() -> dict:
    ventanas = obtener_ventanas_comparables()

    if not ventanas:
        return {
            "actual": 0.0,
            "anterior": None,
            "cambio_puntos": None,
        }

    actuales = obtener_interacciones_reales(
        desde_utc=ventanas["actual_desde"],
        hasta_utc=ventanas["actual_hasta"] + timedelta(seconds=1),
    )

    anteriores = obtener_interacciones_reales(
        desde_utc=ventanas["anterior_desde"],
        hasta_utc=ventanas["anterior_hasta"] + timedelta(seconds=1),
    )

    actuales_analizados = [
        item for item in actuales
        if item.get("estado") == "analizado"
    ]

    anteriores_analizados = [
        item for item in anteriores
        if item.get("estado") == "analizado"
    ]

    def porcentaje_positivo(items):
        if not items:
            return None

        positivos = sum(
            1
            for item in items
            if item.get("sentimiento") == "Positivo"
        )

        return round((positivos / len(items)) * 100, 1)

    actual = porcentaje_positivo(actuales_analizados)
    anterior = porcentaje_positivo(anteriores_analizados)

    cambio = (
        round(actual - anterior, 1)
        if actual is not None and anterior is not None
        else None
    )

    return {
        "actual": actual,
        "anterior": anterior,
        "cambio_puntos": cambio,
    }

def calcular_comparacion_usuarios_activos() -> dict:
    ventanas = obtener_ventanas_comparables()

    if not ventanas:
        return {
            "total": 0,
            "actual": 0,
            "anterior": 0,
            "cambio_porcentual": None,
        }

    todas = obtener_interacciones_reales()

    actuales = obtener_interacciones_reales(
        desde_utc=ventanas["actual_desde"],
        hasta_utc=ventanas["actual_hasta"] + timedelta(seconds=1),
    )

    anteriores = obtener_interacciones_reales(
        desde_utc=ventanas["anterior_desde"],
        hasta_utc=ventanas["anterior_hasta"] + timedelta(seconds=1),
    )

    def autores_unicos(items):
        return {
            item.get("author_id")
            for item in items
            if item.get("author_id")
        }

    total = len(autores_unicos(todas))
    actual = len(autores_unicos(actuales))
    anterior = len(autores_unicos(anteriores))

    if anterior == 0:
        cambio = None
    else:
        cambio = round(
            ((actual - anterior) / anterior) * 100,
            1,
        )

    return {
        "total": total,
        "actual": actual,
        "anterior": anterior,
        "cambio_porcentual": cambio,
    }

def calcular_temas_detectados() -> dict:
    interacciones = obtener_interacciones_reales()

    analizados = [
        item
        for item in interacciones
        if item.get("estado") == "analizado"
        and item.get("tema")
    ]

    conteo = {}

    for item in analizados:
        tema = item["tema"]

        if tema == "OTRO":
            continue

        conteo[tema] = conteo.get(tema, 0) + 1

    return {
        "total": len(conteo),
        "distribucion": conteo,
    }
def calcular_temas_nuevos() -> dict:
    ventanas = obtener_ventanas_comparables()

    if not ventanas:
        return {
            "total": 0,
            "temas": [],
            "sin_base_comparativa": True,
        }

    actuales = obtener_interacciones_reales(
        desde_utc=ventanas["actual_desde"],
        hasta_utc=ventanas["actual_hasta"] + timedelta(seconds=1),
    )

    anteriores = obtener_interacciones_reales(
        desde_utc=ventanas["anterior_desde"],
        hasta_utc=ventanas["anterior_hasta"] + timedelta(seconds=1),
    )

    temas_actuales = {
        item.get("tema")
        for item in actuales
        if item.get("tema") and item.get("tema") != "OTRO"
    }

    temas_anteriores = {
        item.get("tema")
        for item in anteriores
        if item.get("tema") and item.get("tema") != "OTRO"
    }

    # Si no hubo mensajes en la ventana anterior,
    # no afirmamos que todos los temas actuales sean "nuevos".
    if not anteriores:
        return {
            "total": 0,
            "temas": [],
            "sin_base_comparativa": True,
        }

    nuevos = sorted(temas_actuales - temas_anteriores)

    return {
        "total": len(nuevos),
        "temas": nuevos,
        "sin_base_comparativa": False,
    }

def obtener_historico_mensajes(interacciones: list[dict]) -> list[dict]:
    """Agrupa por fecha local las mismas interacciones del KPI."""
    dias: dict[str, int] = {}

    for item in interacciones:
        enviado_en = item.get("enviado_en")
        if not enviado_en:
            continue

        try:
            fecha = datetime.fromisoformat(
                str(enviado_en).replace("Z", "+00:00")
            )
            if fecha.tzinfo is None:
                continue
            fecha_local = fecha.astimezone(ZONA_PROYECTO)
        except (TypeError, ValueError, OverflowError):
            continue

        clave = fecha_local.date().isoformat()
        dias[clave] = dias.get(clave, 0) + 1

    return [
        {"date": fecha, "messages": dias[fecha]}
        for fecha in sorted(dias)
    ]


def obtener_historico_audiencia(interacciones: list[dict]) -> list[dict]:
    """Cuenta autores unicos acumulados por su primera fecha local valida."""
    primeras_fechas: dict[str, str] = {}

    for item in interacciones:
        autor = item.get("author_id")
        if not autor:
            continue

        enviado_en = item.get("enviado_en")
        if not enviado_en:
            continue

        try:
            fecha = datetime.fromisoformat(
                str(enviado_en).replace("Z", "+00:00")
            )
            if fecha.tzinfo is None:
                continue
            dia = fecha.astimezone(ZONA_PROYECTO).date().isoformat()
        except (TypeError, ValueError, OverflowError):
            continue

        if autor not in primeras_fechas or dia < primeras_fechas[autor]:
            primeras_fechas[autor] = dia

    nuevos_por_dia: dict[str, int] = {}

    for dia in primeras_fechas.values():
        nuevos_por_dia[dia] = nuevos_por_dia.get(dia, 0) + 1

    acumulado = 0
    historico = []

    for dia in sorted(nuevos_por_dia):
        acumulado += nuevos_por_dia[dia]
        historico.append({
            "date": dia,
            "audience": acumulado,
        })

    return historico


def obtener_historico_sentimiento(interacciones: list[dict]) -> list[dict]:
    """Porcentaje positivo acumulado de mensajes analizados con fechas reales."""
    dias: dict[str, dict[str, int]] = {}

    for item in interacciones:
        if item.get("estado") != "analizado":
            continue

        try:
            fecha = datetime.fromisoformat(
                str(item.get("enviado_en")).replace("Z", "+00:00")
            )

            if fecha.tzinfo is None:
                return []

            dia = fecha.astimezone(ZONA_PROYECTO).date().isoformat()

        except (TypeError, ValueError, OverflowError):
            return []

        if dia not in dias:
            dias[dia] = {"analizados": 0, "positivos": 0}

        dias[dia]["analizados"] += 1

        if item.get("sentimiento") == "Positivo":
            dias[dia]["positivos"] += 1

    acumulado_analizados = 0
    acumulado_positivos = 0
    historico = []

    for dia in sorted(dias):
        acumulado_analizados += dias[dia]["analizados"]
        acumulado_positivos += dias[dia]["positivos"]

        historico.append({
            "date": dia,
            "sentiment": round(
                acumulado_positivos / acumulado_analizados * 100,
                1,
            ),
        })

    return historico


def obtener_historico_temas(interacciones: list[dict]) -> list[dict]:
    """Cuenta temas distintos acumulados por primera fecha local valida."""
    primeras_fechas = {}

    for item in interacciones:
        if item.get("estado") != "analizado":
            continue

        tema = item.get("tema")

        if not tema or tema == "OTRO":
            continue

        try:
            fecha = datetime.fromisoformat(
                str(item.get("enviado_en")).replace("Z", "+00:00")
            )

            if fecha.tzinfo is None:
                return []

            dia = fecha.astimezone(ZONA_PROYECTO).date().isoformat()

        except (TypeError, ValueError, OverflowError):
            return []

        if tema not in primeras_fechas or dia < primeras_fechas[tema]:
            primeras_fechas[tema] = dia

    nuevos_por_dia = {}

    for dia in primeras_fechas.values():
        nuevos_por_dia[dia] = nuevos_por_dia.get(dia, 0) + 1

    acumulado = 0
    historico = []

    for dia in sorted(nuevos_por_dia):
        acumulado += nuevos_por_dia[dia]

        historico.append({
            "date": dia,
            "topics": acumulado,
        })

    return historico


def obtener_historico_temas_nuevos(
    interacciones: list[dict],
) -> list[dict]:
    """
    Historico semanal de temas nuevos frente a la semana anterior.

    Solo cuenta temas de mensajes analizados.
    Una semana sin mensajes en la anterior no tiene base comparable.
    """
    from collections import defaultdict

    mensajes_por_semana = defaultdict(int)
    temas_por_semana = defaultdict(set)
    semanas = set()

    for item in interacciones:
        valor = item.get("enviado_en")

        try:
            fecha = datetime.fromisoformat(
                str(valor).replace("Z", "+00:00")
            )

            if fecha.tzinfo is None:
                return []

            fecha_local = fecha.astimezone(ZONA_PROYECTO)

        except (TypeError, ValueError, OverflowError):
            return []

        lunes = (
            fecha_local.date()
            - timedelta(days=fecha_local.weekday())
        )

        semanas.add(lunes)
        mensajes_por_semana[lunes] += 1

        tema = str(item.get("tema") or "").strip()

        if (
            item.get("estado") == "analizado"
            and tema
            and tema != "OTRO"
        ):
            temas_por_semana[lunes].add(tema)

    if not semanas:
        return []

    primera = min(semanas)
    ultima = max(semanas)
    cursor = primera
    resultado = []

    while cursor <= ultima:
        anterior = cursor - timedelta(days=7)
        comparable = mensajes_por_semana[anterior] > 0

        if comparable:
            nuevos = (
                temas_por_semana[cursor]
                - temas_por_semana[anterior]
            )

            cantidad = len(nuevos)
        else:
            cantidad = None

        resultado.append({
            "week": cursor.isoformat(),
            "new_topics": cantidad,
            "comparable": comparable,
        })

        cursor += timedelta(days=7)

    return resultado



def obtener_dashboard() -> dict:
    interacciones = obtener_interacciones_reales()

    interacciones_foro = listar_interacciones(limite=None)

    import os
    canales_foro_reales = {
        valor.strip()
        for valor in os.getenv(
            "CLOUDEDTECH_DISCORD_EDUCATIONAL_CHANNEL_IDS", ""
        ).split(",")
        if valor.strip().isdigit()
    }

    metricas_foro = calcular_interacciones_foro(
        interacciones_foro,
        canales_reales=canales_foro_reales,
    )


    analizados = [
        item
        for item in interacciones
        if item.get("estado") == "analizado"
    ]

    total_mensajes = len(interacciones)

    positivos = sum(
        1
        for item in analizados
        if item.get("sentimiento") == "Positivo"
    )

    sentimiento_positivo = (
        round((positivos / len(analizados)) * 100, 1)
        if analizados
        else 0.0
    )

    comparacion_mensajes = calcular_comparacion_mensajes()
    comparacion_sentimiento = calcular_comparacion_sentimiento()
    usuarios = calcular_comparacion_usuarios_activos()
    temas = calcular_temas_detectados()
    temas_nuevos = calcular_temas_nuevos()

    return {
        "forum_interactions": metricas_foro,
        "messages_processed": total_mensajes,
        "messages_history": obtener_historico_mensajes(interacciones),
        "messages_change": comparacion_mensajes["cambio_porcentual"],

        "total_audience": usuarios["total"],
        "audience_history": obtener_historico_audiencia(interacciones),
        "audience_change": usuarios["cambio_porcentual"],

        "positive_sentiment": sentimiento_positivo,
        "sentiment_history": obtener_historico_sentimiento(interacciones),
        "sentiment_change": comparacion_sentimiento["cambio_puntos"],

        "topics_detected": temas["total"],
        "topics_history": obtener_historico_temas(interacciones),
        "new_topics_history": obtener_historico_temas_nuevos(interacciones),
        "new_topics": temas_nuevos["total"],

        "content_generated": contar_contenidos(),
        "pending_approvals": contar_contenidos("pendiente_revision"),
    }

def obtener_distribucion_sentimiento() -> list[dict]:
    interacciones = obtener_interacciones_reales()

    analizados = [
        item
        for item in interacciones
        if item.get("estado") == "analizado"
        and item.get("sentimiento")
    ]

    total = len(analizados)

    conteo = {
        "Positivo": 0,
        "Neutral": 0,
        "Negativo": 0,
    }

    for item in analizados:
        sentimiento = item.get("sentimiento")

        if sentimiento in conteo:
            conteo[sentimiento] += 1

    if total == 0:
        return [
            {"name": nombre, "value": 0.0}
            for nombre in conteo
        ]

    return [
        {
            "name": nombre,
            "value": round((cantidad / total) * 100, 1),
        }
        for nombre, cantidad in conteo.items()
    ]

def obtener_distribucion_temas() -> list[dict]:
    datos = calcular_temas_detectados()
    distribucion = datos["distribucion"]

    total = sum(distribucion.values())

    if total == 0:
        return []

    return [
        {
            "topic": tema,
            "percentage": round((cantidad / total) * 100, 1),
        }
        for tema, cantidad in sorted(
            distribucion.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

def obtener_evolucion_sentimiento() -> list[dict]:
    interacciones = obtener_interacciones_reales()

    analizados = [
        item
        for item in interacciones
        if item.get("estado") == "analizado"
        and item.get("sentimiento")
        and item.get("enviado_en")
    ]

    dias = {}

    for item in analizados:
        sentimiento = str(item["sentimiento"]).strip().lower()

        categorias = {
            "positivo": "positivos",
            "neutral": "neutrales",
            "negativo": "negativos",
        }

        categoria = categorias.get(sentimiento)

        if categoria is None:
            continue

        fecha = datetime.fromisoformat(item["enviado_en"])
        fecha_local = fecha.astimezone(ZONA_PROYECTO)
        clave = fecha_local.date()

        if clave not in dias:
            dias[clave] = {
                "total": 0,
                "positivos": 0,
                "neutrales": 0,
                "negativos": 0,
            }

        dias[clave]["total"] += 1
        dias[clave][categoria] += 1

    nombres_dias = {
        0: "Lun",
        1: "Mar",
        2: "Mi?",
        3: "Jue",
        4: "Vie",
        5: "S?b",
        6: "Dom",
    }

    resultado = []

    for fecha in sorted(dias):
        datos = dias[fecha]
        total = datos["total"]

        resultado.append({
            "day": nombres_dias[fecha.weekday()],
            "date": fecha.isoformat(),
            "positive": round(
                datos["positivos"] / total * 100, 1
            ),
            "neutral": round(
                datos["neutrales"] / total * 100, 1
            ),
            "negative": round(
                datos["negativos"] / total * 100, 1
            ),
            "messages": total,
        })

    return resultado


def obtener_actividad_audiencia() -> dict:
    interacciones = obtener_interacciones_reales()

    horas = [
        "00:00",
        "04:00",
        "08:00",
        "12:00",
        "16:00",
        "20:00",
    ]

    nombres_dias = [
        "Lun",
        "Mar",
        "Mié",
        "Jue",
        "Vie",
        "Sáb",
        "Dom",
    ]

    conteos = {
        dia: [0, 0, 0, 0, 0, 0]
        for dia in nombres_dias
    }

    for item in interacciones:
        enviado_en = item.get("enviado_en")

        if not enviado_en:
            continue

        fecha = datetime.fromisoformat(enviado_en)
        fecha_local = fecha.astimezone(ZONA_PROYECTO)

        dia = nombres_dias[fecha_local.weekday()]

        indice_hora = min(fecha_local.hour // 4, 5)

        conteos[dia][indice_hora] += 1

    maximo = max(
        (
            cantidad
            for valores in conteos.values()
            for cantidad in valores
        ),
        default=0,
    )

    data = []

    for dia in nombres_dias:
        counts = conteos[dia]

        values = [
            round((cantidad / maximo) * 100)
            if maximo > 0
            else 0
            for cantidad in counts
        ]

        data.append({
            "day": dia,
            "values": values,
            "counts": counts,
        })

    return {
        "hours": horas,
        "data": data,
    }

def extraer_hashtags(temas_clave: str | None) -> list[str]:
    if not temas_clave:
        return []

    hashtags = re.findall(
        r"#([\wáéíóúñÁÉÍÓÚÑ-]+)",
        temas_clave,
    )

    resultado = []
    vistos = set()

    for hashtag in hashtags:
        normalizado = hashtag.strip().lower()

        if not normalizado or normalizado == "n/a":
            continue

        if normalizado not in vistos:
            vistos.add(normalizado)
            resultado.append(normalizado)

    return resultado

def obtener_hashtags() -> list[dict]:
    interacciones = obtener_interacciones_reales()
    ventanas = obtener_ventanas_comparables()

    if not ventanas:
        return []

    interacciones_actuales = obtener_interacciones_reales(
        desde_utc=ventanas["actual_desde"],
        hasta_utc=ventanas["actual_hasta"] + timedelta(seconds=1),
    )

    interacciones_anteriores = obtener_interacciones_reales(
        desde_utc=ventanas["anterior_desde"],
        hasta_utc=ventanas["anterior_hasta"] + timedelta(seconds=1),
    )

    def contar_hashtags(interacciones_periodo):
        conteo = {}

        for item in interacciones_periodo:
            if item.get("estado") != "analizado":
                continue

            for hashtag in extraer_hashtags(
                item.get("temas_clave")
            ):
                conteo[hashtag] = conteo.get(hashtag, 0) + 1

        return conteo

    conteo_actual = contar_hashtags(interacciones_actuales)
    conteo_anterior = contar_hashtags(interacciones_anteriores)

    estadisticas = {}

    for item in interacciones:
        if item.get("estado") != "analizado":
            continue

        hashtags = extraer_hashtags(
            item.get("temas_clave")
        )

        for hashtag in hashtags:
            if hashtag not in estadisticas:
                estadisticas[hashtag] = {
                    "mentions": 0,
                    "positive": 0,
                }

            estadisticas[hashtag]["mentions"] += 1

            if item.get("sentimiento") == "Positivo":
                estadisticas[hashtag]["positive"] += 1

    resultado = []

    for indice, (hashtag, datos) in enumerate(
        sorted(
            estadisticas.items(),
            key=lambda item: item[1]["mentions"],
            reverse=True,
        ),
        start=1,
    ):
        sentiment = round(
            (datos["positive"] / datos["mentions"]) * 100,
            1,
        )

        actual = conteo_actual.get(hashtag, 0)
        anterior = conteo_anterior.get(hashtag, 0)

        if anterior > 0:
            growth = round(
                ((actual - anterior) / anterior) * 100,
                1,
            )
        else:
            growth = None

        resultado.append({
            "id": indice,
            "name": f"#{hashtag}",
            "mentions": datos["mentions"],
            "sentiment": sentiment,
            "growth": growth,
        })

    return resultado