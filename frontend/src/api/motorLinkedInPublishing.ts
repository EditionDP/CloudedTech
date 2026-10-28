import { apiRequest } from './client'

export type LinkedInContentMode = 'texto' | 'texto_imagen' | 'imagen'

export interface LinkedInPublishResponse {
    status: 'publicado'
    contenido_id: number
    post_urn: string
}

export async function publishApprovedLinkedInContent(
    contentId: number,
    tipoContenido: LinkedInContentMode,
): Promise<LinkedInPublishResponse> {
    if (!Number.isInteger(contentId) || contentId <= 0) {
        throw new Error('Identificador de contenido invalido')
    }

    if (!['texto', 'texto_imagen', 'imagen'].includes(tipoContenido)) {
        throw new Error('Modalidad de publicacion LinkedIn invalida')
    }

    return await apiRequest(
        `/api/v1/linkedin/oauth/publish/${contentId}`,
        {
            method: 'POST',
            body: JSON.stringify({
                tipo_contenido: tipoContenido,
            }),
        },
    ) as LinkedInPublishResponse
}