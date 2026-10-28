import { useEffect, useMemo, useState } from 'react'
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { apiRequest } from '../api/client'

type MotorMessage = {
  message?: {
    message_id?: string
    channel_name?: string
    created_at?: string
  }
}

type MessagesResponse = {
  total?: number
  messages?: MotorMessage[]
}

type DailyActivity = {
  date: string
  messages: number
  questions: number
}

function normalizeChannel(value: string): string {
  return value.trim().replace(/^#/, '').toLowerCase()
}

function getDateKey(value: string): string | null {
  if (!value) return null

  const parsed = new Date(value)

  if (Number.isNaN(parsed.getTime())) return null

  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Bogota',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(parsed)

  const get = (type: string) =>
    parts.find(part => part.type === type)?.value ?? ''

  const year = get('year')
  const month = get('month')
  const day = get('day')

  return year && month && day
    ? `${year}-${month}-${day}`
    : null
}

export default function MessageActivityChart({
  refreshVersion,
}: {
  refreshVersion: number
}) {
  const [messages, setMessages] = useState<MotorMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const load = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await apiRequest(
          '/api/v1/content-workflow/messages?limit=500',
          { cache: 'no-store' },
        ) as MessagesResponse

        if (!active) return

        setMessages(
          Array.isArray(response.messages)
            ? response.messages
            : [],
        )
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : 'No se pudo consultar la actividad.',
          )
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [refreshVersion])

  const activity = useMemo(() => {
    const daily = new Map<string, DailyActivity>()
    const seen = new Set<string>()

    for (const item of messages) {
      const message = item.message
      if (!message) continue

      const date = getDateKey(message.created_at ?? '')
      if (!date) continue

      const id = (message.message_id ?? '').trim()
      if (id && seen.has(id)) continue
      if (id) seen.add(id)

      const current = daily.get(date) ?? {
        date,
        messages: 0,
        questions: 0,
      }

      current.messages += 1

      const channel = normalizeChannel(message.channel_name ?? '')
      if (channel === 'preguntas' || channel === 'faq') {
        current.questions += 1
      }

      daily.set(date, current)
    }

    return [...daily.values()].sort((a, b) =>
      a.date.localeCompare(b.date),
    )
  }, [messages])

  return (
    <section className="rounded-2xl border border-slate-200 border-t-4 border-t-orange-500 bg-white p-6 shadow-md">
      <h3 className="text-lg font-bold text-[#0F172A]">
        Actividad de mensajes
      </h3>

      <p className="mt-1 text-sm text-slate-500">
        Mensajes y preguntas por día, según los registros recuperados.
      </p>

      <div className="mt-4 flex flex-wrap gap-4 text-xs font-medium">
        <span className="flex items-center gap-2 text-slate-600">
          <span className="h-2.5 w-2.5 rounded-full bg-orange-500" />
          Mensajes
        </span>
        <span className="flex items-center gap-2 text-slate-600">
          <span className="h-2.5 w-2.5 rounded-full bg-violet-500" />
          Preguntas
        </span>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center text-sm text-slate-500">
          Cargando actividad...
        </div>
      ) : error ? (
        <div className="flex h-64 items-center justify-center text-sm text-red-600">
          {error}
        </div>
      ) : activity.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-center text-sm text-slate-500">
          No hay mensajes con fechas válidas para representar.
        </div>
      ) : (
        <div className="mt-5 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={activity}
              margin={{ top: 8, right: 12, left: -18, bottom: 0 }}
            >
              <defs>
                <linearGradient id="messageActivityFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f97316" stopOpacity={0.22} />
                  <stop offset="100%" stopColor="#f97316" stopOpacity={0.01} />
                </linearGradient>
              </defs>

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
                allowDecimals={false}
                domain={[0, 'auto']}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11 }}
              />

              <Tooltip
                labelFormatter={value => `Fecha: ${String(value)}`}
                formatter={(value, name) => [
                  value,
                  name === 'messages' ? 'Mensajes' : 'Preguntas',
                ]}
              />

              <Area
                type="monotone"
                dataKey="messages"
                fill="url(#messageActivityFill)"
                stroke="#f97316"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5 }}
              />

              <Line
                type="monotone"
                dataKey="questions"
                stroke="#8b5cf6"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}

      <p className="mt-3 text-[11px] leading-4 text-slate-500">
        Fuente: hasta 500 mensajes recuperados del Motor IA.
        No representa necesariamente todo el histórico.
        Las preguntas están incluidas en el total de mensajes.
      </p>
    </section>
  )
}
