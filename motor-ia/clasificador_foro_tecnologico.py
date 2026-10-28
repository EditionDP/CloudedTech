"""
Clasificacion conservadora de consultas educativas tecnologicas.

No realiza solicitudes de red, no consulta modelos IA y no publica
respuestas en Discord.
"""

import re
import unicodedata

from filtro_mensajes import es_mensaje_trivial


TEMAS_TECNOLOGICOS = (
    "ia",
    "python",
    "javascript",
    "typescript",
    "react",
    "angular",
    "vue",
    "node",
    "programacion",
    "programar",
    "codigo",
    "software",
    "algoritmo",
    "api",
    "apis",
    "rest",
    "graphql",
    "fastapi",
    "backend",
    "frontend",
    "html",
    "css",
    "sql",
    "nosql",
    "postgresql",
    "mysql",
    "mongodb",
    "base de datos",
    "bases de datos",
    "inteligencia artificial",
    "machine learning",
    "aprendizaje automatico",
    "modelo de lenguaje",
    "llm",
    "red neuronal",
    "redes neuronales",
    "chatbot",
    "agente de ia",
    "agentes de ia",
    "ciberseguridad",
    "seguridad informatica",
    "autenticacion",
    "autorizacion",
    "docker",
    "kubernetes",
    "git",
    "github",
    "cloud computing",
    "computacion en la nube",
    "servidor",
    "servidores",
    "red informatica",
    "redes informaticas",
    "protocolo http",
    "protocolo https",
    "dns",
    "linux",
    "windows server",
    # VOCABULARIO TECNOLOGICO AMPLIADO - PASO 3187
    'rag',
    'retrieval augmented generation',
    'generacion aumentada por recuperacion',
    'computador',
    'computadora',
    'ordenador',
    'pc',
    'hardware',
    'tarjeta grafica',
    'tarjeta de video',
    'gpu',
    'cpu',
    'procesador',
    'microprocesador',
    'memoria ram',
    'ram',
    'memoria rom',
    'placa base',
    'placa madre',
    'motherboard',
    'disco duro',
    'ssd',
    'hdd',
    'nvme',
    'almacenamiento',
    'router',
    'enrutador',
    'switch de red',
    'modem',
    'wifi',
    'ethernet',
    'direccion ip',
    'sistema operativo',
    'windows',
    'macos',
    'android',
    'ios',
    'firmware',
    'bios',
    'uefi',
    'perifericos',
    'teclado',
    'mouse',
    'monitor',
    'pantalla',
    'impresora',
    'internet',
    'navegador web',
    'browser',
    'virtualizacion',
    'maquina virtual',
    'contenedor',
    'transformer',
    'embeddings',
    'embedding',
    'base de datos vectorial',
    'vector database',
    'prompt',
    'ingenieria de prompts',
    'agente inteligente',
    'agentes inteligentes',
    'automatizacion',
    'robotica',
    'iot',
    'internet de las cosas',
    'blockchain',
    'criptografia',
    'phishing',
    'malware',
    'firewall',
    'vpn',
)

INTENCIONES_EDUCATIVAS = (
    "ques",
    "q es",
    "que es",
    "que son",
    "como funciona",
    "como funcionan",
    "como usar",
    "como se usa",
    "como aprender",
    "como puedo aprender",
    "como empezar",
    "como implementar",
    "como configurar",
    "como instalar",
    "como crear",
    "como resolver",
    "como solucionar",
    "cual es la diferencia",
    "que diferencia hay",
    "para que sirve",
    "por que",
    "pueden explicar",
    "puedes explicar",
    "me explican",
    "me explicas",
    "necesito ayuda con",
    "tengo un problema con",
    "tengo problemas con",
    "tengo un error en",
    "no funciona",
    "no funcionan",
    "no puedo",
    "me falla",
    "no conecta",
    "no compila",
    "se bloquea",
    "me sale un error",
    "tengo errores",
    "me aparece un error en",
)


def normalizar(texto: str) -> str:
    if not isinstance(texto, str):
        return ""

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )
    texto = texto.casefold()
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return " ".join(texto.split())


def contiene_expresion(texto: str, expresion: str) -> bool:
    patron = r"(?<!\w)" + re.escape(expresion) + r"(?!\w)"
    return re.search(patron, texto) is not None


def clasificar_consulta(texto: str) -> dict:
    if es_mensaje_trivial(texto):
        return {
            "es_consulta_tecnologica": False,
            "motivo": "mensaje_trivial",
        }

    normalizado = normalizar(texto)

    temas = [
        tema
        for tema in TEMAS_TECNOLOGICOS
        if contiene_expresion(normalizado, tema)
    ]

    intenciones = [
        intencion
        for intencion in INTENCIONES_EDUCATIVAS
        if contiene_expresion(normalizado, intencion)
    ]

    if not temas:
        motivo = "sin_tema_tecnologico"
    elif not intenciones:
        motivo = "sin_intencion_educativa"
    else:
        motivo = "consulta_tecnologica"

    return {
        "es_consulta_tecnologica": bool(temas and intenciones),
        "motivo": motivo,
        "temas": temas,
        "intenciones": intenciones,
    }
