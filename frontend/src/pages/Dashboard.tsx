import MessageActivityChart from '../charts/MessageActivityChart'
import { apiRequest } from '../api/client'
import { useEffect, useState } from 'react'
import {
  CheckCircle,
  FileText,
  MessageSquare,
  RefreshCw,
  Sparkles,
  Tag,
  Users,
} from 'lucide-react'

import DashboardKpiCard from '../components/DashboardKpiCard'
import SentimentChart from '../charts/SentimentChart'
import TopicsChart from '../charts/TopicsChart'
import DashboardCommunityInsights from '../components/DashboardCommunityInsights'
import SentimentEvolution from '../charts/SentimentEvolution'
import AudienceHeatmap from '../charts/AudienceHeatmap'

type DashboardData = {
  forum_interactions?: {
    total: number
    discord_real: number
    comunidad_simulada: number
    criterio: string
  }
  messages_processed: number

  messages_history?: Array<{ date: string; messages: number }>
  messages_change: number | null
  total_audience: number
  audience_history?: Array<{ date: string; audience: number }>
  audience_change: number | null
  positive_sentiment: number
  sentiment_history?: Array<{ date: string; sentiment: number }>
  sentiment_change: number | null
  topics_detected: number
  topics_history?: Array<{ date: string; topics: number }>
  new_topics_history?: Array<{
    week: string
    new_topics: number | null
    comparable: boolean
  }>
  new_topics: number
  content_generated: number
  pending_approvals: number
}



function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [refreshing, setRefreshing] = useState(false)
  const [analyticsVersion, setAnalyticsVersion] = useState(0)

  const loadDashboard = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)

    try {
      setError(null)

      const [data] = await Promise.all([
        apiRequest('/api/v1/content-workflow/dashboard', {
          cache: 'no-store',
        }) as Promise<DashboardData>,
        apiRequest('/api/v1/content-workflow/analytics', {
          cache: 'no-store',
        }),
      ])

      setDashboardData(data)
      setAnalyticsVersion((version) => version + 1)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Error desconocido al cargar el dashboard'
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    void loadDashboard()
  }, [])

  if (loading) {
    return <div className="p-6 text-slate-500">Cargando dashboard...</div>
  }

  if (!dashboardData) {
    return (
      <div className="p-6 text-red-600">
        {error ?? 'No hay datos disponibles'}
      </div>
    )
  }



  return (
    <div>

      {/* Encabezado */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Dashboard
          </h2>
          <p className="mt-1 text-slate-500">
            Resumen de tu comunidad
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadDashboard(true)}
          disabled={refreshing}
          className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
        >
          <RefreshCw
            size={16}
            className={refreshing ? 'animate-spin' : ''}
          />
          {refreshing ? 'Actualizando...' : 'Actualizar datos'}
        </button>
      </div>

      {error && (
        <p role="alert" className="mt-3 text-sm text-red-600">
          {error}. Se muestran los ultimos datos disponibles.
        </p>
      )}


      {/* KPIs */}
      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 2xl:grid-cols-7">

        <DashboardKpiCard
          title="Interacciones del Foro"
          value={
            dashboardData.forum_interactions
              ? dashboardData.forum_interactions.total.toLocaleString('es-CO')
              : 'N/D'
          }
          description={
            dashboardData.forum_interactions
              ? `Discord real: ${dashboardData.forum_interactions.discord_real.toLocaleString('es-CO')}`
              : 'Esperando métricas del Foro'
          }
          icon={<MessageSquare size={20} />}
        />

        <DashboardKpiCard
          title="Mensajes procesados"
          value={dashboardData.messages_processed.toLocaleString("es-CO")}
          description={
            dashboardData.messages_change === null
              ? 'Sin comparación'
              : `${dashboardData.messages_change > 0 ? '+' : ''}${dashboardData.messages_change.toLocaleString('es-CO')}% esta semana`
          }
          icon={<MessageSquare size={20} />}
        
          history={dashboardData?.messages_history}
        />

        <DashboardKpiCard
          title="Total de audiencia"
          value={dashboardData.total_audience.toLocaleString("es-CO")}
          description={
            dashboardData.audience_change === null
              ? 'Sin comparación'
              : `${dashboardData.audience_change > 0 ? '+' : ''}${dashboardData.audience_change.toLocaleString('es-CO')}% esta semana`
          }
          icon={<Users size={20} />}
        history={dashboardData?.audience_history}
          historyDataKey="audience"
        />


        <DashboardKpiCard
          title="Sentimiento positivo"
          value={`${dashboardData.positive_sentiment}%`}
          description={
            dashboardData.sentiment_change === null
              ? 'Sin comparación'
              : `${dashboardData.sentiment_change > 0 ? '+' : ''}${dashboardData.sentiment_change.toLocaleString('es-CO')} puntos esta semana`
          }
          icon={<Sparkles size={20} />}
        history={dashboardData?.sentiment_history}
          historyDataKey="sentiment"
        />


        <DashboardKpiCard
          title="Temas detectados"
          value={dashboardData.topics_detected.toString()}
          description={
            dashboardData.new_topics_history?.length &&
            dashboardData.new_topics_history.at(-1)?.comparable === false
              ? 'Sin base comparativa para temas nuevos'
              : `${dashboardData.new_topics} nuevos temas`
          }
          icon={<Tag size={20} />}
          history={dashboardData?.topics_history}
          historyDataKey="topics"
        />

        <div className="min-w-0 rounded-2xl border border-slate-700 bg-slate-900 p-3 shadow-lg">
          <p className="mb-2 text-xs font-medium text-slate-300">
            Evolución semanal de temas nuevos
          </p>
          <DashboardKpiCard
            title="Temas nuevos"
            value={
              dashboardData.new_topics_history?.at(-1)?.comparable === false
                ? 'N/D'
                : dashboardData.new_topics.toLocaleString('es-CO')
            }
            description="Comparación con la semana anterior"
            icon={<Tag size={20} />}
            history={dashboardData.new_topics_history?.map(item => ({
              date: item.week,
              week: item.week,
              new_topics: item.new_topics,
              comparable: item.comparable,
            }))}
            historyDataKey="new_topics"
          />
        </div>


        <DashboardKpiCard
          title="Contenidos generados"
          value={dashboardData.content_generated.toString()}
          description="Esta semana"
          icon={<FileText size={20} />}
        />


        <DashboardKpiCard
          title="Pendientes"
          value={dashboardData.pending_approvals.toString()}
          description="Requieren aprobación"
          icon={<CheckCircle size={20} />}
        />
        

      </div>
      
             
      <div className="mt-6 grid grid-cols-1 items-start gap-5 lg:grid-cols-2">
        <DashboardCommunityInsights refreshVersion={analyticsVersion} />

        <MessageActivityChart refreshVersion={analyticsVersion} />

        <SentimentEvolution key={analyticsVersion} />
        <SentimentChart key={analyticsVersion} />

        <div className="lg:col-span-2">
          <TopicsChart key={analyticsVersion} />
        </div>

        <div className="lg:col-span-2">
          <AudienceHeatmap key={analyticsVersion} />
        </div>
      </div>

    </div>
  )
}

export default Dashboard
