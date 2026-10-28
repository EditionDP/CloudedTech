import { apiRequest } from './client'

export type SimulationTopic =
  | 'ia'
  | 'programacion'
  | 'ciberseguridad'
  | 'datos'
  | 'mixto'

export type SimulationPace = 'bajo' | 'medio' | 'alto'

export interface SimulationState {
  estado: string
  tema?: SimulationTopic
  ritmo?: SimulationPace
  participantes?: number
  mensajes_generados?: number
  origen_comunidad?: string
  es_simulado?: boolean
  publicar_discord?: boolean
  [key: string]: unknown
}

export interface SimulationActionResponse {
  cambio_realizado: boolean
  motivo?: string
  estado: SimulationState
}

const BASE_URL = '/api/v1/content-workflow/simulation'

export async function getCommunitySimulationStatus(): Promise<SimulationState> {
  return apiRequest(`${BASE_URL}/status`, {
    method: 'GET',
  }) as Promise<SimulationState>
}

export async function startCommunitySimulation(
  tema: SimulationTopic,
  ritmo: SimulationPace,
): Promise<SimulationActionResponse> {
  return apiRequest(`${BASE_URL}/start`, {
    method: 'POST',
    body: JSON.stringify({ tema, ritmo }),
  }) as Promise<SimulationActionResponse>
}

export async function stopCommunitySimulation(): Promise<SimulationActionResponse> {
  return apiRequest(`${BASE_URL}/stop`, {
    method: 'POST',
  }) as Promise<SimulationActionResponse>
}

// PARTICIPANTES ADMINISTRABLES - PASO 3162

export interface SimulationParticipant {
  id: string
  nombre: string
  activo: boolean
  avatar_url: string | null
  eliminado: boolean
  es_simulado: boolean
}

export interface SimulationParticipantsResponse {
  participantes: SimulationParticipant[]
  total: number
  activos: number
  inactivos: number
}

export interface CreateSimulationParticipant {
  nombre: string
  avatar_url?: string | null
}

export interface UpdateSimulationParticipant {
  nombre?: string
  activo?: boolean
  avatar_url?: string | null
}

export async function getSimulationParticipants():
  Promise<SimulationParticipantsResponse> {
  return apiRequest(`${BASE_URL}/participants`, {
    method: 'GET',
  }) as Promise<SimulationParticipantsResponse>
}

export async function createSimulationParticipant(
  data: CreateSimulationParticipant,
): Promise<SimulationParticipant> {
  return apiRequest(`${BASE_URL}/participants`, {
    method: 'POST',
    body: JSON.stringify(data),
  }) as Promise<SimulationParticipant>
}

export async function updateSimulationParticipant(
  id: string,
  data: UpdateSimulationParticipant,
): Promise<SimulationParticipant> {
  return apiRequest(
    `${BASE_URL}/participants/${encodeURIComponent(id)}`,
    {
      method: 'PATCH',
      body: JSON.stringify(data),
    },
  ) as Promise<SimulationParticipant>
}

export async function deleteSimulationParticipant(
  id: string,
): Promise<{ id: string; eliminado: boolean }> {
  return apiRequest(
    `${BASE_URL}/participants/${encodeURIComponent(id)}`,
    {
      method: 'DELETE',
    },
  ) as Promise<{ id: string; eliminado: boolean }>
}


// CONFIGURACION DISCORD - PASO 3183

export type DiscordSimulationChannel =
  | 'general'
  | 'faq'
  | 'pqrs'
  | 'notificaciones'
  | 'chat-egresados'
  | 'oportunidades-laborales'
  | 'foro-educativo'


export interface DiscordSimulationConfig {
  habilitado: boolean
  canal: DiscordSimulationChannel
  guild_id: string
  guild_name: string
  canales: DiscordSimulationChannel[]
}

export interface UpdateDiscordSimulationConfig {
  habilitado?: boolean
  canal?: DiscordSimulationChannel
  canales?: DiscordSimulationChannel[]
}

export async function getDiscordSimulationConfig():
  Promise<DiscordSimulationConfig> {
  return apiRequest(`${BASE_URL}/discord/config`, {
    method: 'GET',
  }) as Promise<DiscordSimulationConfig>
}

export async function updateDiscordSimulationConfig(
  data: UpdateDiscordSimulationConfig,
): Promise<DiscordSimulationConfig> {
  return apiRequest(`${BASE_URL}/discord/config`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }) as Promise<DiscordSimulationConfig>
}


export const DISCORD_SIMULATION_CHANNELS: ReadonlyArray<{
  id: DiscordSimulationChannel
  nombre: string
}> = [
  { id: 'general', nombre: 'General' },
  { id: 'faq', nombre: 'Preguntas frecuentes' },
  { id: 'pqrs', nombre: 'PQRS' },
  { id: 'notificaciones', nombre: 'Notificaciones' },
  { id: 'chat-egresados', nombre: 'Chat de egresados' },
  { id: 'oportunidades-laborales', nombre: 'Oportunidades laborales' },
  { id: 'foro-educativo', nombre: 'Foro educativo' },
]
