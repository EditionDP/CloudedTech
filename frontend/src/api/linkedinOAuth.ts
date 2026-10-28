import { apiRequest } from './client'

const CALLBACK_ORIGIN = 'http://localhost:5174'
const CALLBACK_TYPE = 'CLOUDEDTECH_LINKEDIN_OAUTH_CALLBACK'

type AuthorizationResponse = {
  authorization_url: string
  expires_in_seconds: number
}

export type LinkedInAuthorizationCode = {
  code: string
  state: string
}

export async function iniciarConexionLinkedIn(): Promise<LinkedInAuthorizationCode> {
  // Abrir durante el gesto del usuario para reducir bloqueos del navegador.
  const popup = window.open(
    'about:blank',
    'cloudedtech-linkedin-oauth',
    'width=620,height=760',
  )

  if (!popup) {
    throw new Error('El navegador bloqueo la ventana de LinkedIn.')
  }

  try {
    const respuesta = await apiRequest(
      '/api/v1/linkedin/oauth/start',
      { method: 'GET' },
    ) as AuthorizationResponse

    const url = new URL(respuesta.authorization_url)

    if (
      url.origin !== 'https://www.linkedin.com' ||
      url.pathname !== '/oauth/v2/authorization'
    ) {
      throw new Error('La URL de autorizacion no es valida.')
    }

    const expectedState = url.searchParams.get('state')

    if (!expectedState) {
      throw new Error('LinkedIn OAuth no devolvio un state.')
    }

    const ttl = Math.min(
      Math.max(respuesta.expires_in_seconds || 600, 1),
      600,
    ) * 1000

    return await new Promise<LinkedInAuthorizationCode>(
      (resolve, reject) => {
        let finished = false

        const cleanup = () => {
          window.removeEventListener('message', onMessage)
          window.clearTimeout(timeout)
          window.clearInterval(closedCheck)
        }

        const fail = (message: string) => {
          if (finished) return
          finished = true
          cleanup()
          popup.close()
          reject(new Error(message))
        }

        const onMessage = (event: MessageEvent) => {
          if (
            event.origin !== CALLBACK_ORIGIN ||
            event.source !== popup
          ) {
            return
          }

          const data = event.data

          if (
            !data ||
            data.type !== CALLBACK_TYPE ||
            typeof data.code !== 'string' ||
            typeof data.state !== 'string' ||
            !data.code ||
            data.state !== expectedState
          ) {
            return
          }

          if (finished) return
          finished = true
          cleanup()
          popup.close()

          resolve({
            code: data.code,
            state: data.state,
          })
        }

        const timeout = window.setTimeout(
          () => fail('La autorizacion de LinkedIn vencio.'),
          ttl,
        )

        const closedCheck = window.setInterval(() => {
          if (popup.closed) {
            fail('Se cerro la ventana de autorizacion.')
          }
        }, 500)

        window.addEventListener('message', onMessage)

        popup.location.replace(url.toString())
      },
    )
  } catch (error) {
    popup.close()
    throw error
  }
}


export type LinkedInConnectionResult = {
  status: string
  message: string
}

export async function completarConexionLinkedIn(
  authorization: LinkedInAuthorizationCode,
): Promise<LinkedInConnectionResult> {
  if (!authorization.code || !authorization.state) {
    throw new Error('La autorizacion de LinkedIn es invalida.')
  }

  return apiRequest(
    '/api/v1/linkedin/oauth/complete',
    {
      method: 'POST',
      body: JSON.stringify({
        code: authorization.code,
        state: authorization.state,
      }),
    },
  ) as Promise<LinkedInConnectionResult>
}
