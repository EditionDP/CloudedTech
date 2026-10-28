import { useState } from 'react'
import { apiRequest } from '../api/client'

type Props = {
    open: boolean
    onClose: () => void
}

const topics = [
    { value: 'api', label: 'API' },
    { value: 'python', label: 'Python' },
    { value: 'sql', label: 'SQL' },
    { value: 'inteligencia artificial', label: 'Inteligencia artificial' },
    { value: 'docker', label: 'Docker' },
    { value: 'postgresql', label: 'PostgreSQL' },
    { value: 'ciberseguridad', label: 'Ciberseguridad' },
    { value: 'react', label: 'React' },
]

export default function EducationalPublicationModal({ open, onClose }: Props) {
    const [topic, setTopic] = useState('python')
    const [title, setTitle] = useState('')
    const [content, setContent] = useState('')
    const [preview, setPreview] = useState(false)

    const [generating, setGenerating] = useState(false)
    const [generationError, setGenerationError] = useState('')

    const [saving, setSaving] = useState(false)
    const [saveError, setSaveError] = useState('')
    const [savedId, setSavedId] = useState<number | null>(null)

    async function generarContenidoEducativo() {
        if (generating || saving || savedId !== null) return

        setGenerating(true)
        setGenerationError('')

        try {
            const respuesta = (await apiRequest(
                '/api/v1/content-workflow/generate-original',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        tema: topic,
                        instrucciones:
                            'Crea una publicacion educativa original sobre el tema. ' +
                            'Explica un concepto concreto con claridad, incluye ' +
                            'un ejemplo practico y termina con una pregunta. ' +
                            'No inventes hechos ni atribuyas mensajes a personas.',
                        formato: 'discord',
                        tono: 'educativo',
                    }),
                },
            )) as { titulo?: string; contenido?: string }

            const tituloNuevo = String(respuesta.titulo ?? '').trim()
            const contenidoNuevo = String(respuesta.contenido ?? '').trim()

            if (!tituloNuevo || !contenidoNuevo) {
                throw new Error('La IA no devolvio contenido valido.')
            }

            if (tituloNuevo.length > 200 || contenidoNuevo.length > 10000) {
                throw new Error('El contenido generado supera el limite permitido.')
            }

            setTitle(tituloNuevo)
            setContent(contenidoNuevo)
            setPreview(true)
        } catch (error) {
            setGenerationError(
                error instanceof Error
                    ? error.message
                    : 'No fue posible generar contenido.',
            )
        } finally {
            setGenerating(false)
        }
    }

    async function guardarBorradorEducativo() {
        if (saving || savedId !== null) return

        const titulo = title.trim()
        const contenido = content.trim()

        if (!titulo || !contenido) {
            setSaveError('Debes completar el título y el contenido.')
            return
        }

        setSaving(true)
        setSaveError('')

        try {
            const response = (await apiRequest(
                '/api/v1/content-workflow/educational/publications',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        tema: topic,
                        titulo,
                        contenido,
                    }),
                },
            )) as { id?: number; publicacion_id?: number }

            const id = response.id ?? response.publicacion_id

            if (typeof id !== 'number' || !Number.isInteger(id) || id <= 0) {
                throw new Error(
                    'El servidor no devolvió un identificador válido. ' +
                    'Comprueba el registro antes de intentar guardar nuevamente.',
                )
            }

            setSavedId(id)
        } catch (error) {
            setSaveError(
                error instanceof Error
                    ? error.message
                    : 'No fue posible guardar el borrador.',
            )
        } finally {
            setSaving(false)
        }
    }

    if (!open) return null

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4"
            role="presentation"
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) onClose()
            }}
        >
            <section
                role="dialog"
                aria-modal="true"
                aria-labelledby="educational-publication-title"
                className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl"
            >
                <div className="mb-5 flex items-start justify-between gap-4">
                    <div>
                        <h2
                            id="educational-publication-title"
                            className="text-xl font-bold text-slate-900"
                        >
                            Publicación educativa multired
                        </h2>
                        <p className="mt-1 text-sm text-slate-500">
                            Prepara contenido para Discord, X y LinkedIn.
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-lg border border-slate-200 px-3 py-1 text-sm text-slate-600"
                    >
                        Cerrar
                    </button>
                </div>

                <div className="space-y-4">
                    <label className="block text-sm font-semibold text-slate-700">
                        Tema tecnológico
                        <select
                            value={topic}
                            disabled={saving || generating || savedId !== null}
                            onChange={(event) => {
                                setTopic(event.target.value)
                                setTitle('')
                                setContent('')
                                setPreview(false)
                                setGenerationError('')
                            }}
                            className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-3 py-2"
                        >
                            {topics.map((item) => (
                                <option key={item.value} value={item.value}>
                                    {item.label}
                                </option>
                            ))}
                        </select>
                    </label>

                    <div className="flex flex-wrap items-center gap-3">
                        <button
                            type="button"
                            disabled={generating || saving || savedId !== null}
                            onClick={generarContenidoEducativo}
                            className="rounded-xl bg-orange-500 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
                        >
                            {generating
                                ? 'Generando contenido...'
                                : title.trim() || content.trim()
                                  ? 'Regenerar con IA'
                                  : 'Generar con IA'}
                        </button>
                        <p className="text-xs text-slate-500">
                            La IA prepara el contenido. Puedes editarlo antes de guardarlo.
                        </p>
                    </div>

                    {generationError && (
                        <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                            {generationError}
                        </div>
                    )}

                    <label className="block text-sm font-semibold text-slate-700">
                        Título
                        <input
                            value={title}
                            disabled={saving || generating || savedId !== null}
                            maxLength={200}
                            onChange={(event) => {
                                setTitle(event.target.value)
                                setPreview(false)
                            }}
                            placeholder="Título de la publicación"
                            className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2"
                        />
                    </label>

                    <label className="block text-sm font-semibold text-slate-700">
                        Contenido
                        <textarea
                            value={content}
                            disabled={saving || generating || savedId !== null}
                            maxLength={10000}
                            rows={8}
                            onChange={(event) => {
                                setContent(event.target.value)
                                setPreview(false)
                            }}
                            placeholder="Escribe el contenido educativo..."
                            className="mt-2 w-full resize-y rounded-xl border border-slate-300 px-3 py-2"
                        />
                    </label>

                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                        <p className="text-sm font-semibold text-slate-800">
                            Plataformas previstas
                        </p>
                        <p className="mt-2 text-sm text-slate-600">
                            Discord · X · LinkedIn
                        </p>
                        <p className="mt-2 text-xs text-amber-700">
                            El envío real estará disponible después de conectar
                            las API oficiales y sus permisos.
                        </p>
                    </div>

                    {preview && (
                        <div className="rounded-xl border border-orange-200 bg-orange-50 p-4">
                            <p className="mb-2 text-xs font-bold uppercase text-orange-700">
                                Vista previa
                            </p>
                            <h3 className="font-bold text-slate-900">
                                {title.trim()}
                            </h3>
                            <p className="mt-3 whitespace-pre-wrap text-sm text-slate-700">
                                {content.trim()}
                            </p>
                        </div>
                    )}

                    {savedId !== null && (
                        <div
                            role="status"
                            className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800"
                        >
                            Borrador educativo #{savedId} guardado correctamente.
                            Todavía no se ha publicado en ninguna red.
                        </div>
                    )}

                    {saveError && (
                        <div
                            role="alert"
                            className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"
                        >
                            {saveError}
                        </div>
                    )}
                    <div className="flex flex-wrap justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
                        >
                            Cancelar
                        </button>
                        <button
                            type="button"
                            disabled={!title.trim() || !content.trim()}
                            onClick={() => setPreview(true)}
                            className="rounded-xl bg-slate-800 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
                        >
                            Vista previa
                        </button>
                        <button
                            type="button"
                            disabled={saving || generating || savedId !== null || !title.trim() || !content.trim()}
                            onClick={guardarBorradorEducativo}
                            className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
                        >
                            {saving ? 'Guardando...' : savedId !== null ? 'Borrador guardado' : 'Guardar borrador'}
                        </button>
                        <button
                            type="button"
                            disabled
                            title="Pendiente de conectar el backend"
                            className="cursor-not-allowed rounded-xl bg-orange-500 px-4 py-2 text-sm font-semibold text-white opacity-50"
                        >
                            Confirmar publicación
                        </button>
                    </div>
                </div>
            </section>
        </div>
    )
}