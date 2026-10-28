import { useEffect, useMemo, useState } from 'react'
import { apiRequest } from '../api/client'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

type ActivityRow = {
  day: string
  values: number[]
  counts: number[]
}

type ActivityHeatmap = {
  hours: string[]
  data: ActivityRow[]
}

type AnalyticsResponse = {
  activity_heatmap?: ActivityHeatmap
}

type HourlyActivity = {
  hour: string
  range: string
  messages: number
}

function AudienceHeatmap() {
  const [activity, setActivity] = useState<ActivityHeatmap | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const loadActivity = async () => {
      setLoading(true)
      setError(null)

      try {
        const result = await apiRequest(
          '/api/v1/content-workflow/analytics',
          { cache: 'no-store' },
        ) as AnalyticsResponse

        if (!active) return

        setActivity(result.activity_heatmap ?? null)
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : 'Error al cargar la actividad de audiencia.',
          )
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    void loadActivity()

    return () => {
      active = false
    }
  }, [])

  const hourly = useMemo<HourlyActivity[]>(() => {
    if (
      !activity ||
      !Array.isArray(activity.hours) ||
      !Array.isArray(activity.data)
    ) {
      return []
    }

    return activity.hours.map((hour, index) => {
      const total = activity.data.reduce((sum, row) => {
        const value = row.counts?.[index]

        return sum + (
          typeof value === 'number' &&
          Number.isFinite(value) &&
          value >= 0
            ? value
            : 0
        )
      }, 0)

      const start = Number(hour.split(':')[0])
      const end = Number.isFinite(start)
        ? `${String(Math.min(start + 3, 23)).padStart(2, '0')}:59`
        : ''

      return {
        hour,
        range: `${hour}\u2013${end}`,
        messages: total,
      }
    })
  }, [activity])

  const maxMessages = Math.max(
    0,
    ...hourly.map(item => item.messages),
  )

  const peak = maxMessages > 0
    ? hourly.find(item => item.messages === maxMessages)
    : undefined

  const totalMessages = hourly.reduce(
    (sum, item) => sum + item.messages,
    0,
  )

  return (
    <section className="rounded-2xl border border-slate-200 border-t-4 border-t-orange-500 bg-white p-6 shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-bold text-[#0F172A]">
            Actividad de audiencia
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Mensajes registrados por franja horaria de cuatro horas.
          </p>
        </div>

        {peak && (
          <div className="rounded-xl border border-orange-200 bg-orange-50 px-3 py-2">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-orange-700">
              Mayor actividad
            </p>
            <p className="text-sm font-bold text-orange-800">
              {peak.range}
            </p>
            <p className="text-xs text-orange-700">
              {peak.messages} mensajes
            </p>
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex h-72 items-center justify-center text-sm text-slate-500">
          Cargando actividad...
        </div>
      ) : error ? (
        <div className="flex h-72 items-center justify-center text-center text-sm text-red-600">
          {error}
        </div>
      ) : hourly.length === 0 || totalMessages === 0 ? (
        <div className="flex h-72 items-center justify-center text-center text-sm text-slate-500">
          No hay mensajes registrados para calcular la actividad horaria.
        </div>
      ) : (
        <div className="mt-5 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={hourly}
              margin={{ top: 10, right: 12, left: -12, bottom: 5 }}
              barCategoryGap="28%"
            >
              <CartesianGrid
                stroke="#e2e8f0"
                strokeDasharray="3 4"
                vertical={false}
              />

              <XAxis
                dataKey="hour"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12 }}
              />

              <YAxis
                allowDecimals={false}
                domain={[0, 'auto']}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />

              <Tooltip
                labelFormatter={value => {
                  const item = hourly.find(
                    entry => entry.hour === String(value),
                  )
                  return item?.range ?? String(value)
                }}
                formatter={value => [value, 'Mensajes']}
              />

              <Bar
                dataKey="messages"
                name="Mensajes"
                radius={[7, 7, 0, 0]}
                maxBarSize={64}
              >
                {hourly.map(item => (
                  <Cell
                    key={item.hour}
                    fill={
                      item.messages === maxMessages
                        ? '#f97316'
                        : '#334155'
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <p className="mt-3 text-[11px] leading-4 text-slate-500">
        Fuente: actividad registrada por el Motor IA, agrupada
        en franjas de cuatro horas de Colombia.
        Los conteos se acumulan por día de la semana.
      </p>
    </section>
  )
}

export default AudienceHeatmap
