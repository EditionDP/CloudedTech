import { useCallback, useEffect, useState } from 'react'
import { Play, RefreshCw, Square, Users } from 'lucide-react'
import {
  getCommunitySimulationStatus,
  getDiscordSimulationConfig,
  updateDiscordSimulationConfig,
  DISCORD_SIMULATION_CHANNELS,
  getSimulationParticipants,
  startCommunitySimulation,
  stopCommunitySimulation,
} from '../api/communitySimulation'
import type {
  DiscordSimulationChannel,
  DiscordSimulationConfig,
  SimulationPace,
  SimulationState,
  SimulationTopic,
} from '../api/communitySimulation'

function obtenerEstado(respuesta: unknown): SimulationState {
  if (respuesta && typeof respuesta === 'object') {
    const datos = respuesta as Record<string, unknown>
    if (datos.estado && typeof datos.estado === 'object') {
      return datos.estado as SimulationState
    }
    return datos as SimulationState
  }
  throw new Error('Respuesta de estado no valida.')
}

import CommunitySimulationParticipants from './CommunitySimulationParticipants'

export default function CommunitySimulationSettings() {
  // PASO 3197: INTERFAZ MULTICANAL DISCORD
  const [discordConfig, setDiscordConfig] = useState<DiscordSimulationConfig | null>(null)
  const [canalesDiscord, setCanalesDiscord] = useState<DiscordSimulationChannel[]>([])
  const [guardandoDiscord, setGuardandoDiscord] = useState(false)
  const [errorDiscord, setErrorDiscord] = useState('')
  const [mensajeDiscord, setMensajeDiscord] = useState('')

  const [tema, setTema] = useState<SimulationTopic>('mixto')
  const [ritmo, setRitmo] = useState<SimulationPace>('medio')
  const [estado, setEstado] = useState<SimulationState | null>(null)
  const [cargando, setCargando] = useState(true)
  const [procesando, setProcesando] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  // PASO 3166: CONTROL PARTICIPANTES ACTIVOS
  const [participantesActivos, setParticipantesActivos] = useState<number | null>(null)

  const actualizar = useCallback(async () => {
    setCargando(true)
    setError('')
    try {
      const [respuesta, participantes] = await Promise.all([
        getCommunitySimulationStatus(),
        getSimulationParticipants(),
      ])
      setEstado(obtenerEstado(respuesta))
      setParticipantesActivos(participantes.activos)
      try {
        const config = await getDiscordSimulationConfig()
        setDiscordConfig(config)
        setCanalesDiscord(config.canales ?? [config.canal])
        setErrorDiscord('')
      } catch (discordError) {
        setDiscordConfig(null)
        setCanalesDiscord([])
        setErrorDiscord(
          discordError instanceof Error
            ? discordError.message
            : 'No fue posible consultar la configuracion de Discord.',
        )
      }
    } catch (e) {
      setParticipantesActivos(null)
      setError(e instanceof Error ? e.message : 'No fue posible consultar el simulador.')
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    void actualizar()
  }, [actualizar])

  const ejecutando = estado?.estado === 'ejecutando'
  const detenido = estado?.estado === 'detenido'
  const ocupado = cargando || procesando

  function cambiarCanalDiscord(
    canal: DiscordSimulationChannel,
    seleccionado: boolean,
  ) {
    setMensajeDiscord('')
    setCanalesDiscord((actuales) =>
      seleccionado
        ? Array.from(new Set([...actuales, canal]))
        : actuales.filter((actual) => actual !== canal),
    )
  }

  // PASO 3198: CONTROL PUBLICACION REAL
  async function cambiarPublicacionDiscord(habilitado: boolean) {
    if (
      ocupado ||
      guardandoDiscord ||
      !detenido ||
      !discordConfig
    ) return

    if (
      habilitado &&
      !window.confirm(
        'Vas a habilitar publicaciones REALES en el servidor CloudEDTech_OF. ' +
        'Los mensajes generados por la simulacion podran aparecer en Discord. ' +
        '?Deseas continuar?',
      )
    ) return

    setGuardandoDiscord(true)
    setErrorDiscord('')
    setMensajeDiscord('')

    try {
      const actualizado = await updateDiscordSimulationConfig({
        habilitado,
        canales: canalesDiscord,
      })
      setDiscordConfig(actualizado)
      setCanalesDiscord(actualizado.canales ?? [actualizado.canal])
      setMensajeDiscord(
        habilitado
          ? 'Publicacion real habilitada en la configuracion del Motor IA.'
          : 'Publicacion real deshabilitada.',
      )
    } catch (e) {
      setErrorDiscord(
        e instanceof Error
          ? e.message
          : 'No fue posible actualizar la publicacion real.',
      )
    } finally {
      setGuardandoDiscord(false)
    }
  }

  async function guardarCanalesDiscord() {
    if (
      ocupado ||
      guardandoDiscord ||
      !detenido ||
      !discordConfig ||
      canalesDiscord.length === 0
    ) return

    setGuardandoDiscord(true)
    setErrorDiscord('')
    setMensajeDiscord('')

    try {
      const actualizado = await updateDiscordSimulationConfig({
        canales: canalesDiscord,
      })
      setDiscordConfig(actualizado)
      setCanalesDiscord(actualizado.canales ?? [actualizado.canal])
      setMensajeDiscord('Destinos de Discord guardados correctamente.')
    } catch (e) {
      setErrorDiscord(
        e instanceof Error
          ? e.message
          : 'No fue posible guardar los destinos de Discord.',
      )
    } finally {
      setGuardandoDiscord(false)
    }
  }

  async function iniciar() {
    if (ocupado || !detenido || participantesActivos === null || participantesActivos === 0) return
    setProcesando(true)
    setError('')
    setMensaje('')
    try {
      const respuesta = await startCommunitySimulation(tema, ritmo)
      setEstado(obtenerEstado(respuesta))
      setMensaje(
        respuesta.cambio_realizado
          ? 'Solicitud de inicio enviada al Motor IA. Consulta el estado para verificar el generador.'
          : 'La simulacion ya estaba iniciada.',
      )
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No fue posible iniciar.')
    } finally {
      setProcesando(false)
    }
  }

  async function detener() {
    if (ocupado || !ejecutando) return
    setProcesando(true)
    setError('')
    setMensaje('')
    try {
      const respuesta = await stopCommunitySimulation()
      setEstado(obtenerEstado(respuesta))
      setMensaje(
        respuesta.cambio_realizado
          ? 'Estado de simulacion detenido.'
          : 'La simulacion ya estaba detenida.',
      )
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No fue posible detener.')
    } finally {
      setProcesando(false)
    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-orange-100 text-orange-600">
            <Users size={22} />
          </div>
          <div>
            <h2 className="font-semibold text-slate-900">Comunidad Simulada - Demo</h2>
            <p className="text-sm text-slate-500">
              {participantesActivos === null ? 'Consultando participantes...' : `${participantesActivos} participantes activos para conversaciones tecnologicas`}
            </p>
          </div>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
          ejecutando
            ? 'bg-green-100 text-green-700'
            : detenido
              ? 'bg-slate-100 text-slate-700'
              : 'bg-amber-100 text-amber-700'
        }`}>
          {cargando ? 'Consultando...' : estado?.estado ?? 'Sin conexion'}
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-xs text-slate-500">Participantes</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{participantesActivos ?? "?"}</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-xs text-slate-500">Origen</p>
          <p className="mt-1 text-sm font-semibold text-slate-800">discord_demo</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-xs text-slate-500">Publicacion en Discord</p>
          <p className={`mt-1 text-sm font-semibold ${
            discordConfig?.habilitado ? 'text-orange-700' : 'text-green-700'
          }`}>
            {discordConfig === null
              ? 'Sin verificar'
              : discordConfig.habilitado
                ? 'Habilitada'
                : 'Deshabilitada'}
          </p>
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <label className="block text-sm font-medium text-slate-700">
          Tema de conversacion
          <select
            value={tema}
            onChange={(e) => setTema(e.target.value as SimulationTopic)}
            disabled={ocupado || ejecutando}
            className="mt-2 w-full rounded-lg border border-slate-200 px-4 py-3 outline-none focus:border-orange-500 disabled:opacity-60"
          >
            <option value="mixto">Mixto</option>
            <option value="ia">Inteligencia artificial</option>
            <option value="programacion">Programacion</option>
            <option value="ciberseguridad">Ciberseguridad</option>
            <option value="datos">Datos</option>
          </select>
        </label>

        <label className="block text-sm font-medium text-slate-700">
          Ritmo de participacion
          <select
            value={ritmo}
            onChange={(e) => setRitmo(e.target.value as SimulationPace)}
            disabled={ocupado || ejecutando}
            className="mt-2 w-full rounded-lg border border-slate-200 px-4 py-3 outline-none focus:border-orange-500 disabled:opacity-60"
          >
            <option value="bajo">Bajo</option>
            <option value="medio">Medio</option>
            <option value="alto">Alto</option>
          </select>
        </label>
      </div>

      <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold text-slate-900">
              Destinos de Discord
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              Servidor: {discordConfig?.guild_name ?? 'CloudEDTech_OF'}.
              Selecciona los canales permitidos para la demostracion.
            </p>
          </div>
          <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-600">
            {canalesDiscord.length} de {DISCORD_SIMULATION_CHANNELS.length} seleccionados
          </span>
        </div>

        <label className="mt-4 flex cursor-pointer items-center gap-3 text-sm font-semibold text-slate-800">
          <input
            type="checkbox"
            checked={canalesDiscord.length === DISCORD_SIMULATION_CHANNELS.length}
            disabled={ocupado || guardandoDiscord || !detenido || !discordConfig}
            onChange={(e) => {
              setMensajeDiscord('')
              setCanalesDiscord(
                e.target.checked
                  ? DISCORD_SIMULATION_CHANNELS.map((destino) => destino.id)
                  : [],
              )
            }}
            className="h-4 w-4 accent-orange-500"
          />
          Seleccionar todos los destinos
        </label>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {DISCORD_SIMULATION_CHANNELS.map((destino) => (
            <label
              key={destino.id}
              className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-700"
            >
              <input
                type="checkbox"
                checked={canalesDiscord.includes(destino.id)}
                disabled={ocupado || guardandoDiscord || !detenido || !discordConfig}
                onChange={(e) => cambiarCanalDiscord(destino.id, e.target.checked)}
                className="h-4 w-4 accent-orange-500"
              />
              {destino.nombre}
            </label>
          ))}
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-4 rounded-lg border border-orange-200 bg-orange-50 p-4">
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Publicacion real en Discord
            </p>
            <p className="mt-1 text-xs text-slate-600">
              Al habilitarla, la simulacion podra publicar mensajes
              en los destinos autorizados de CloudEDTech_OF.
            </p>
          </div>
          <label className="flex items-center gap-3 text-sm font-semibold text-slate-800">
            <input
              type="checkbox"
              checked={discordConfig?.habilitado ?? false}
              disabled={
                ocupado ||
                guardandoDiscord ||
                !detenido ||
                !discordConfig ||
                canalesDiscord.length === 0
              }
              onChange={(e) => void cambiarPublicacionDiscord(e.target.checked)}
              className="h-5 w-5 accent-orange-500"
            />
            {discordConfig?.habilitado ? 'Discord activo' : 'Discord inactivo'}
          </label>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => void guardarCanalesDiscord()}
            disabled={
              ocupado ||
              guardandoDiscord ||
              !detenido ||
              !discordConfig ||
              canalesDiscord.length === 0
            }
            className="rounded-lg bg-orange-500 px-5 py-3 text-sm font-semibold text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {guardandoDiscord ? 'Guardando...' : 'Guardar destinos'}
          </button>
          <span className="text-xs text-slate-500">
            Guardar destinos no activa la publicacion real.
          </span>
        </div>

        {errorDiscord && (
          <p role="alert" className="mt-3 text-sm text-red-700">
            {errorDiscord}
          </p>
        )}
        {mensajeDiscord && (
          <p role="status" className="mt-3 text-sm text-green-700">
            {mensajeDiscord}
          </p>
        )}
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => void iniciar()}
          disabled={ocupado || !detenido || participantesActivos === null || participantesActivos === 0}
          className="flex items-center gap-2 rounded-lg bg-orange-500 px-5 py-3 text-sm font-semibold text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Play size={17} /> Iniciar
        </button>
        <button
          type="button"
          onClick={() => void detener()}
          disabled={ocupado || !ejecutando}
          className="flex items-center gap-2 rounded-lg border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Square size={17} /> Detener
        </button>
        <button
          type="button"
          onClick={() => void actualizar()}
          disabled={ocupado}
          className="flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-3 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-50"
        >
          <RefreshCw size={17} /> Actualizar estado
        </button>
      </div>

      {error && (
        <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}
      {mensaje && (
        <p role="status" className="mt-4 rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
          {mensaje}
        </p>
      )}

      <p className="mt-4 text-xs text-slate-500">
        Entorno de demostracion. Consulta el estado del Motor IA para verificar el generador.
        La publicacion real depende de la configuracion del Motor IA y no se activa al guardar destinos.
      </p>
      <CommunitySimulationParticipants
        ejecutando={ejecutando || !detenido}
        onParticipantsChanged={setParticipantesActivos}
      />
    </section>
  )
}