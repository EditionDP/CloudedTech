import type { ReactNode } from 'react'
import { Line, LineChart, ResponsiveContainer, Tooltip } from 'recharts'

type DashboardKpiCardProps = {
  title: string
  value: string
  description: string
  icon: ReactNode
  history?: Array<{
    date: string
    messages?: number
    audience?: number
    sentiment?: number
    topics?: number
    week?: string
    new_topics?: number | null
    comparable?: boolean
  }>
  historyDataKey?: 'messages' | 'audience' | 'sentiment' | 'topics' | 'new_topics'
}

const accents: Record<string, string> = {
  'Mensajes procesados': 'text-white',
  'Total de audiencia': 'text-sky-300',
  'Sentimiento positivo': 'text-emerald-300',
  'Temas detectados': 'text-orange-300',
  'Contenidos generados': 'text-violet-300',
  'Pendientes': 'text-amber-300',
}

export default function DashboardKpiCard({
  title,
  value,
  description,
  icon,
  history,
  historyDataKey = 'messages',
}: DashboardKpiCardProps) {
  const accent = accents[title] ?? 'text-white'
  const hasHistory = Array.isArray(history)
  const isWeeklyHistory = historyDataKey === 'new_topics'

  const validHistory = (history ?? [])
    .filter(item => {
      const period = isWeeklyHistory ? item.week : item.date
      const value = item[historyDataKey]

      return (
        typeof period === 'string' &&
        /^\d{4}-\d{2}-\d{2}$/.test(period) &&
        (!isWeeklyHistory || item.comparable === true) &&
        typeof value === 'number' &&
        Number.isFinite(value) &&
        value >= 0
      )
    })
    .map(item => ({
      ...item,
      date: isWeeklyHistory ? item.week! : item.date,
    }))
    .sort((a, b) => a.date.localeCompare(b.date))

  const canDrawTrend =
    new Set(validHistory.map(item => item.date)).size >= 2

  const hasMissingComparison =
    isWeeklyHistory &&
    (history ?? []).some(item => item.comparable === false) &&
    validHistory.length === 0

  return (
    <article className="relative min-w-0 overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 p-3 shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:border-orange-500/60">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-orange-500 to-sky-500" />

      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-xs font-medium leading-4 text-slate-300">
            {title}
          </p>
          <p className={`mt-2 break-words text-2xl font-bold tracking-tight ${accent}`}>
            {value}
          </p>
        </div>

        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-orange-500/15 text-orange-400">
          {icon}
        </div>
      </div>

      {hasHistory && (
        <div className="mt-2">
          {canDrawTrend ? (
            <div
              className="h-10 w-full"
              role="img"
              aria-label={`Tendencia histórica de ${title}`}
            >
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={validHistory}
                  margin={{ top: 4, right: 2, bottom: 4, left: 2 }}
                >
                  <Tooltip
                    labelFormatter={label =>
                      `${isWeeklyHistory ? 'Semana del' : 'Fecha:'} ${String(label)}`
                    }
                    formatter={value => [
                      value,
                      historyDataKey === 'audience'
                        ? 'Usuarios ?nicos'
                        : historyDataKey === 'sentiment'
                          ? 'Sentimiento positivo (%)'
                          : historyDataKey === 'topics'
                            ? 'Temas distintos'
                            : historyDataKey === 'new_topics'
                              ? 'Temas nuevos por semana'
                              : 'Mensajes',
                    ]}
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      border: '1px solid #334155',
                      borderRadius: 10,
                      color: '#f8fafc',
                      fontSize: 11,
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey={historyDataKey}
                    stroke="#f97316"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 3 }}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-[10px] text-slate-500">
              {hasMissingComparison
                ? 'Sin base comparativa'
                : 'Hist?rico insuficiente'}
            </p>
          )}
        </div>
      )}
      <p className="mt-2 text-[11px] leading-4 text-slate-400">
        {description}
      </p>
    </article>
  )
}