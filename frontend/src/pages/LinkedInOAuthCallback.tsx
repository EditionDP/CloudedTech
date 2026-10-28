import { useEffect, useState } from 'react'

type CallbackStatus = 'processing' | 'delivered' | 'error'

const LOCAL_ORIGIN = window.location.origin

export default function LinkedInOAuthCallback() {
  const [status, setStatus] = useState<CallbackStatus>('processing')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const state = params.get('state')
    const error = params.get('error')

    // Evitar que los parametros OAuth permanezcan en la barra de direcciones.
    window.history.replaceState(
      {},
      document.title,
      window.location.pathname,
    )

    if (error || !code || !state) {
      setStatus('error')
      return
    }

    if (!window.opener || window.opener.closed) {
      setStatus('error')
      return
    }

    try {
      window.opener.postMessage(
        {
          type: 'CLOUDEDTECH_LINKEDIN_OAUTH_CALLBACK',
          code,
          state,
        },
        LOCAL_ORIGIN,
      )

      setStatus('delivered')
    } catch {
      setStatus('error')
    }
  }, [])

  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background: '#0F172A',
        color: '#F8FAFC',
        fontFamily: 'Inter, sans-serif',
        padding: '24px',
      }}
    >
      <section style={{ maxWidth: 480, textAlign: 'center' }}>
        <h1>CloudEdTech ? LinkedIn</h1>

        {status === 'processing' && (
          <p>Procesando el retorno de autorizaci?n...</p>
        )}

        {status === 'delivered' && (
          <p>
            La respuesta de LinkedIn se envi? a la ventana local.
            Regresa a CloudEdTech para continuar.
          </p>
        )}

        {status === 'error' && (
          <p>
            No fue posible completar el retorno de LinkedIn.
            Regresa a CloudEdTech e inicia nuevamente la conexi?n.
          </p>
        )}
      </section>
    </main>
  )
}
