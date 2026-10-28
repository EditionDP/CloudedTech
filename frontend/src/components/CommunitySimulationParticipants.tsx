import { useCallback, useEffect, useState } from 'react'
import { Pencil, Plus, Trash2, UserRound, Users } from 'lucide-react'
import {
  createSimulationParticipant,
  deleteSimulationParticipant,
  getSimulationParticipants,
  updateSimulationParticipant,
} from '../api/communitySimulation'
import type { SimulationParticipant } from '../api/communitySimulation'

interface Props {
  ejecutando: boolean
  onParticipantsChanged?: (activeCount: number) => void
}

export default function CommunitySimulationParticipants({
  ejecutando,
  onParticipantsChanged,
}: Props) {
  const [usuarios, setUsuarios] = useState<SimulationParticipant[]>([])
  const [busqueda, setBusqueda] = useState('')
  const [cargando, setCargando] = useState(true)
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [editando, setEditando] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [formulario, setFormulario] = useState(false)

  const actualizar = useCallback(async () => {
    setCargando(true)
    try {
      const datos = await getSimulationParticipants()
      setUsuarios(datos.participantes)
      onParticipantsChanged?.(datos.activos)
      setError('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error consultando participantes.')
    } finally {
      setCargando(false)
    }
  }, [onParticipantsChanged])

  useEffect(() => {
    void actualizar()
  }, [actualizar])

  const activos = usuarios.filter((u) => u.activo).length
  const visibles = usuarios.filter((u) =>
    u.nombre.toLowerCase().includes(busqueda.toLowerCase()),
  )
  const bloqueado = ejecutando || cargando || guardando

  async function ejecutarAccion(
    accion: () => Promise<unknown>,
    texto: string,
  ) {
    setGuardando(true)
    setError('')
    setMensaje('')
    try {
      await accion()
      setMensaje(texto)
      await actualizar()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo guardar el cambio.')
    } finally {
      setGuardando(false)
    }
  }

  async function guardar() {
    const valor = nombre.trim()
    if (valor.length < 2 || bloqueado) return

    await ejecutarAccion(
      () => editando
        ? updateSimulationParticipant(editando, { nombre: valor })
        : createSimulationParticipant({ nombre: valor }),
      editando ? 'Participante actualizado.' : 'Participante creado.',
    )
    setFormulario(false)
    setEditando(null)
    setNombre('')
  }

  async function cambiarTodos(activo: boolean) {
    if (bloqueado) return
    await ejecutarAccion(async () => {
      for (const usuario of usuarios) {
        if (usuario.activo !== activo) {
          await updateSimulationParticipant(usuario.id, { activo })
        }
      }
    }, activo ? 'Participantes habilitados.' : 'Participantes deshabilitados.')
  }

  async function eliminar(usuario: SimulationParticipant) {
    if (bloqueado) return
    if (!window.confirm(`Eliminar al participante virtual "${usuario.nombre}"?`)) return

    await ejecutarAccion(
      () => deleteSimulationParticipant(usuario.id),
      'Participante eliminado de futuras simulaciones.',
    )
  }

  return (
    <div className="mt-6 rounded-xl border border-slate-200 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="flex items-center gap-2 font-semibold text-slate-900">
            <Users size={19} className="text-orange-500" />
            Administracion de participantes
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            Selecciona quienes podran interactuar en cada simulacion.
          </p>
        </div>
        <button
          type="button"
          disabled={bloqueado}
          onClick={() => {
            setEditando(null)
            setNombre('')
            setFormulario(true)
          }}
          className="flex items-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          <Plus size={16} /> Crear usuario
        </button>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-slate-600">
          <strong>{activos}</strong> activos de <strong>{usuarios.length}</strong> participantes
        </p>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={bloqueado}
            onClick={() => void cambiarTodos(true)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-xs disabled:opacity-50"
          >
            Todos
          </button>
          <button
            type="button"
            disabled={bloqueado}
            onClick={() => void cambiarTodos(false)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-xs disabled:opacity-50"
          >
            Ninguno
          </button>
        </div>
      </div>

      <input
        value={busqueda}
        onChange={(e) => setBusqueda(e.target.value)}
        placeholder="Buscar participante..."
        className="mt-4 w-full rounded-lg border border-slate-200 px-4 py-2 text-sm outline-none focus:border-orange-500"
      />

      {formulario && (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            void guardar()
          }}
          className="mt-4 rounded-lg bg-slate-50 p-4"
        >
          <label className="text-sm font-medium text-slate-700">
            Nombre del participante virtual
            <input
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              maxLength={80}
              className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
            />
          </label>
          <div className="mt-3 flex gap-2">
            <button
              type="submit"
              disabled={bloqueado || nombre.trim().length < 2}
              className="rounded-lg bg-orange-500 px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              Guardar
            </button>
            <button
              type="button"
              onClick={() => setFormulario(false)}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm"
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {error && <p role="alert" className="mt-3 text-sm text-red-600">{error}</p>}
      {mensaje && <p role="status" className="mt-3 text-sm text-green-700">{mensaje}</p>}

      <div className="mt-4 max-h-80 overflow-y-auto rounded-lg border border-slate-200">
        {visibles.map((usuario) => (
          <div
            key={usuario.id}
            className="flex items-center gap-3 border-b border-slate-100 px-3 py-3 last:border-b-0"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100">
              <UserRound size={17} className="text-slate-500" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-800">{usuario.nombre}</p>
              <p className="text-xs text-slate-400">
                {usuario.activo ? 'Habilitado' : 'Deshabilitado'}
              </p>
            </div>
            <label className="relative inline-flex cursor-pointer items-center">
              <input
                type="checkbox"
                checked={usuario.activo}
                disabled={bloqueado}
                onChange={(e) => void ejecutarAccion(
                  () => updateSimulationParticipant(usuario.id, { activo: e.target.checked }),
                  'Participacion actualizada.',
                )}
                className="peer sr-only"
                aria-label={`Habilitar ${usuario.nombre}`}
              />
              <span className="h-6 w-11 rounded-full bg-slate-300 transition peer-checked:bg-orange-500 peer-disabled:opacity-50 after:absolute after:left-1 after:top-1 after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all peer-checked:after:translate-x-5" />
            </label>
            <button
              type="button"
              disabled={bloqueado}
              onClick={() => {
                setEditando(usuario.id)
                setNombre(usuario.nombre)
                setFormulario(true)
              }}
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 disabled:opacity-50"
              aria-label={`Editar ${usuario.nombre}`}
            >
              <Pencil size={16} />
            </button>
            <button
              type="button"
              disabled={bloqueado}
              onClick={() => void eliminar(usuario)}
              className="rounded-lg p-2 text-red-500 hover:bg-red-50 disabled:opacity-50"
              aria-label={`Eliminar ${usuario.nombre}`}
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
        {!cargando && visibles.length === 0 && (
          <p className="p-4 text-center text-sm text-slate-500">
            No se encontraron participantes.
          </p>
        )}
      </div>
    </div>
  )
}
