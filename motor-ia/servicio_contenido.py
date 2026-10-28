from typing import Literal

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from cerebro_ia import llm


class ContenidoGenerado(BaseModel):
    formato: Literal["linkedin", "newsletter", "x", "discord"]
    titulo: str = Field(description="Título breve y atractivo del contenido")
    contenido: str = Field(description="Contenido final listo para revisión humana")
    llamada_accion: str = Field(description="Llamada a la acción apropiada")
    hashtags: list[str] = Field(
        default_factory=list,
        description="Hashtags relevantes. Vacío si el formato no los necesita",
    )


llm_contenido = llm.with_structured_output(ContenidoGenerado)


template_contenido = """
ERES EL COPYWRITER DE CLOUDEDTECH.

Tu trabajo es transformar una interacción REAL de una comunidad de Discord
en una pieza de contenido de marketing para revisión humana.

INTERACCIÓN ORIGINAL:
"{texto}"

CANAL:
{canal}

FORMATO SOLICITADO:
{formato}

TONO:
{tono}

REGLAS:
1. Conserva el significado de la interacción original.
2. NO inventes estadísticas, testimonios, nombres, empresas, eventos ni hechos.
3. NO presentes como cierta información que no aparezca en la interacción.
4. No incluyas datos privados ni información sensible del autor.
5. El resultado siempre debe quedar pendiente de revisión humana.
6. Escribe en español claro y natural.
7. Evita exageraciones y afirmaciones engañosas.
8. Está PROHIBIDO afirmar que CloudEdTech ya está realizando una acción,
   mejora, investigación o desarrollo si eso no aparece explícitamente
   en la interacción original.
9. Puedes convertir una sugerencia del usuario en una reflexión o invitación,
   pero nunca en una acción ya ejecutada por CloudEdTech.
10. Si falta información para respaldar una afirmación, omítela.

SI EL FORMATO ES "linkedin":
- Genera una publicación profesional y atractiva.
- Usa párrafos breves.
- Incluye una llamada a la acción.
- Incluye entre 3 y 5 hashtags relevantes.

SI EL FORMATO ES "newsletter":
- Genera un título atractivo.
- Desarrolla una introducción y un cuerpo informativo.
- Incluye una llamada a la acción.
- Los hashtags pueden quedar vacíos.

SI EL FORMATO ES "x":
- Genera una publicacion breve y natural para X.
- El contenido completo debe tener como maximo 280 caracteres.
- Evita hashtags innecesarios.
- No inventes datos ni afirmaciones sobre acciones de CloudEdTech.

SI EL FORMATO ES "discord":
- Genera un mensaje cercano, claro y conversacional.
- Mantiene el contexto del mensaje original.
- Invita a participar sin atribuir compromisos a CloudEdTech.
- No incluyas datos privados del autor.

Devuelve exclusivamente la salida estructurada solicitada.
"""



# Generaci?n independiente: no requiere mensajes de Ingesta.
template_contenido_original = """
ERES EL COPYWRITER DE CLOUDEDTECH.

Tu tarea es redactar una publicaci?n ORIGINAL a partir de un tema
seleccionado por el usuario. NO est?s transformando un mensaje de Discord.

TEMA:
{tema}

INSTRUCCIONES ADICIONALES:
{instrucciones}

PLATAFORMA:
{formato}

TONO:
{tono}

REGLAS:
1. Redacta en espa?ol claro, natural y profesional.
2. No inventes mensajes, autores ni conversaciones de Discord.
3. No inventes estad?sticas, eventos, oportunidades, testimonios,
   alianzas, resultados ni anuncios oficiales.
4. No afirmes que CloudEdTech realiz? o realizar? acciones que no
   est?n respaldadas por las instrucciones proporcionadas.
5. Si faltan datos concretos, utiliza un enfoque educativo,
   reflexivo o de invitaci?n a participar.
6. Evita afirmaciones enga?osas y compromisos institucionales.
7. El contenido ser? revisado por una persona antes de publicarse.

SI LA PLATAFORMA ES linkedin:
- Redacta una publicaci?n profesional con p?rrafos breves.
- Incluye una llamada a la acci?n.
- Utiliza entre 3 y 5 hashtags relevantes.

SI LA PLATAFORMA ES x:
- El texto completo debe tener como m?ximo 280 caracteres.
- Prioriza claridad y concisi?n.
- Evita hashtags innecesarios.

SI LA PLATAFORMA ES discord:
- Redacta un mensaje cercano y conversacional.
- Invita a participar sin atribuir declaraciones a miembros reales.
- No presupongas un canal espec?fico ni una conversaci?n previa.

Devuelve exclusivamente la salida estructurada solicitada.
"""

prompt_contenido_original = PromptTemplate(
    input_variables=["tema", "instrucciones", "formato", "tono"],
    template=template_contenido_original,
)

cadena_contenido_original = prompt_contenido_original | llm_contenido

prompt_contenido = PromptTemplate(
    input_variables=["texto", "canal", "formato", "tono"],
    template=template_contenido,
)

cadena_contenido = prompt_contenido | llm_contenido


def generar_contenido(
    texto: str,
    canal: str,
    formato: Literal["linkedin", "newsletter", "x", "discord"],
    tono: str = "profesional",
) -> dict:
    if not texto.strip():
        raise ValueError("El texto de origen no puede estar vacío.")

    respuesta = cadena_contenido.invoke(
        {
            "texto": texto,
            "canal": canal,
            "formato": formato,
            "tono": tono,
        }
    )

    return respuesta.model_dump()


def generar_contenido_original(
    tema: str,
    instrucciones: str,
    formato: Literal["linkedin", "x", "discord"],
    tono: str = "profesional",
) -> dict:
    """
    Genera una publicaci?n original sin interacci?n de Discord.
    El resultado requiere revisi?n humana.
    """
    tema = tema.strip()
    instrucciones = instrucciones.strip()
    tono = tono.strip() or "profesional"

    if not tema:
        raise ValueError("Debes seleccionar un tema para generar contenido.")

    if formato not in {"linkedin", "x", "discord"}:
        raise ValueError("La plataforma solicitada no est? permitida.")

    respuesta = cadena_contenido_original.invoke(
        {
            "tema": tema,
            "instrucciones": instrucciones,
            "formato": formato,
            "tono": tono,
        }
    )

    resultado = respuesta.model_dump()

    if resultado.get("formato") != formato:
        resultado["formato"] = formato

    contenido = str(resultado.get("contenido") or "").strip()

    if not contenido:
        raise ValueError("La IA no devolvi? contenido v?lido.")

    if formato == "x" and len(contenido) > 280:
        raise ValueError(
            "La IA gener? m?s de 280 caracteres para X. "
            "Intenta nuevamente o ajusta las instrucciones."
        )

    resultado["contenido"] = contenido
    return resultado
