import { useEffect, useState } from 'react'
import { apiRequest } from '../api/client'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

type EvolutionItem = {
  day: string
  date: string
  positive: number
  neutral?: number
  negative?: number
  messages: number
}

type AnalyticsResponse = {
  sentiment?: {
    evolution?: EvolutionItem[]
  }
}

const SERIES = [
  { key: 'positive', label: 'Positivo', color: '#22c55e' },
  { key: 'neutral', label: 'Neutral', color: '#94a3b8' },
  { key: 'negative', label: 'Negativo', color: '#ef4444' },
] as const

function SentimentEvolution() {
  const [data, setData] = useState<EvolutionItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const loadEvolution = async () => {
      setLoading(true)
      setError(null)

      try {
        const result = await apiRequest(
          '/api/v1/content-workflow/analytics',
          { cache: 'no-store' },
        ) as AnalyticsResponse

        if (!active) return

        setData(
          Array.isArray(result.sentiment?.evolution)
            ? result.sentiment.evolution
            : [],
        )
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : 'Error al consultar la evolución del sentimiento.',
          )
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    void loadEvolution()

    return () => {
      active = false
    }
  }, [])

  const complete = data.every(item =>
    [item.positive, item.neutral, item.negative].every(
      value => typeof value === 'number'
        && Number.isFinite(value)
        && value >= 0
        && value <= 100,
    ),
  )

  const ready = data.length > 0 && complete

  return (
    <section className="rounded-2xl border border-slate-200 border-t-4 border-t-orange-500 bg-white p-6 shadow-md">
      <h3 className="text-lg font-bold text-[#0F172A]">
        Evolución del sentimiento
      </h3>

      <p className="mt-1 text-sm text-slate-500">
        Porcentaje diario de mensajes analizados por sentimiento.
      </p>

      <div className="mt-4 flex flex-wrap gap-4 text-xs font-medium text-slate-600">
        {SERIES.map(series => (
          <span key={series.key} className="flex items-center gap-2">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: series.color }}
            />
            {series.label}
          </span>
        ))}
      </div>

      {loading ? (
        <div className="flex h-72 items-center justify-center text-sm text-slate-500">
          Cargando evolución Prueba...
        </div>
      ) : error ? (
        <div className="flex h-72 items-center justify-center text-center text-sm text-red-600">
          {error}
        </div>
      ) : data.length === 0 ? (
        <div className="flex h-72 items-center justify-center text-center text-sm text-slate-500">
          No hay mensajes analizados con fechas válidas.
        </div>
      ) : !ready ? (
        <div className="flex h-72 items-center justify-center px-4 text-center text-sm text-amber-700">
          El Motor IA todavía no entrega las tres categorías de sentimiento.
          Verifica que estó ejecutando la versión actualizada.
        </div>
      ) : (
        <div className="mt-5 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 10, right: 12, left: 0, bottom: 5 }}
            >
              <CartesianGrid
                stroke="#e2e8f0"
                strokeDasharray="3 4"
                vertical={false}
              />

              <XAxis
                dataKey="date"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
                tickFormatter={(value: string) => {
                  const [, month, day] = value.split('-')
                  return `${day}/${month}`
                }}
              />

              <YAxis
                domain={[0, 100]}
                ticks={[0, 25, 50, 75, 100]}
                tickFormatter={(value: number) => `${value}%`}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />

              <Tooltip
                labelFormatter={value => `Fecha: ${String(value)}`}
                formatter={(value, name) => {
                  const series = SERIES.find(item => item.key === name)
                  return [`${value}%`, series?.label ?? String(name)]
                }}
              />

              {SERIES.map(series => (
                <Line
                  key={series.key}
                  type="monotone"
                  dataKey={series.key}
                  name={series.key}
                  stroke={series.color}
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <p className="mt-3 text-[11px] text-slate-500">
        Fuente: mensajes analizados por el Motor IA.
        Cada punto representa un día con registros válidos.
      </p>
    </section>
  )
}

export default SentimentEvolution
