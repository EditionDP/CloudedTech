import { getDiscordPublishingChannels } from "../api/motorDiscordPublishing";
import type { DiscordPublishingChannel } from "../api/motorDiscordPublishing";
import { getMotorAiSettings } from "../api/motorAiSettings";
import type { MotorAiSettings } from "../api/motorAiSettings";
import CommunitySimulationSettings from '../components/CommunitySimulationSettings'
import {
  Bell,
  Bot,
  CheckCircle2,
  Cloud,
  Database,
  MessageSquare,
  Save,
  Settings as SettingsIcon,
  ShieldCheck,
  Users,
} from 'lucide-react'

import { useEffect, useState } from "react";
import { getUsers } from "../api/users";
import { getNotificationPreferences, saveNotificationPreferences } from "../api/notificationPreferences";
import type { NotificationPreferences } from "../api/notificationPreferences";
import type { User } from "../api/users";


function Settings() {
  const [users, setUsers] = useState<User[]>([]);

  const [notificationPreferences, setNotificationPreferences] =
    useState<NotificationPreferences>({
      highlights_enabled: false,
      sentiment_enabled: false,
      approvals_enabled: false,
    });

  const [notificationsLoading, setNotificationsLoading] = useState(true);
  const [notificationsSaving, setNotificationsSaving] = useState(false);
  const [notificationsError, setNotificationsError] = useState<string | null>(null);
  const [notificationsMessage, setNotificationsMessage] = useState<string | null>(null);
  useEffect(() => {
    let activo = true;

    async function cargarPreferencias() {
      try {
        const preferencias = await getNotificationPreferences();

        if (!activo) return;

        setNotificationPreferences(preferencias);
        setNotificationsError(null);
      } catch (error) {
        if (!activo) return;

        setNotificationsError(
          error instanceof Error
            ? error.message
            : "No fue posible cargar las preferencias de notificaciones."
        );
      } finally {
        if (activo) setNotificationsLoading(false);
      }
    }

    void cargarPreferencias();

    return () => {
      activo = false;
    };
  }, []);
  const [aiSettings, setAiSettings] = useState<MotorAiSettings | null>(null);
  const [aiLoading, setAiLoading] = useState(true);
  const [aiError, setAiError] = useState<string | null>(null);

  useEffect(() => {
    let activo = true;

    async function cargarConfiguracionIA() {
      try {
        const configuracion = await getMotorAiSettings();

        if (!activo) return;

        setAiSettings(configuracion);
        setAiError(null);
      } catch (error) {
        if (!activo) return;

        setAiSettings(null);
        setAiError(
          error instanceof Error
            ? error.message
            : "No fue posible consultar el Motor IA."
        );
      } finally {
        if (activo) setAiLoading(false);
      }
    }

    void cargarConfiguracionIA();

    return () => {
      activo = false;
    };
  }, []);

  const [discordChannels, setDiscordChannels] = useState<DiscordPublishingChannel[]>([]);
  const [discordChannelId, setDiscordChannelId] = useState("");
  const [discordLoading, setDiscordLoading] = useState(true);
  const [discordError, setDiscordError] = useState<string | null>(null);

  useEffect(() => {
    let activo = true;

    async function cargarCanalesDiscord() {
      try {
        const canales = await getDiscordPublishingChannels();

        if (!activo) return;

        setDiscordChannels(canales);
        setDiscordChannelId((actual) =>
          canales.some((canal) => canal.id === actual)
            ? actual
            : (canales.find((canal) => canal.nombre === "general")?.id ?? canales[0]?.id ?? "")
        );
        setDiscordError(null);
      } catch (error) {
        if (!activo) return;

        setDiscordChannels([]);
        setDiscordChannelId("");
        setDiscordError(
          error instanceof Error
            ? error.message
            : "No fue posible consultar los canales de Discord."
        );
      } finally {
        if (activo) setDiscordLoading(false);
      }
    }

    void cargarCanalesDiscord();

    return () => {
      activo = false;
    };
  }, []);

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await getUsers();
        setUsers(data);
      } catch (error) {
        console.error("No fue posible cargar los usuarios:", error);
      }
    };

    loadUsers();
  }, []);
  return (
    <div className="space-y-8">

      {/* HEADER */}
      <div>
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-orange-100 text-orange-500">
            <SettingsIcon size={22} />
          </div>

          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              Configuración
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              Configura CloudEdTech, la inteligencia artificial y las
              integraciones de la comunidad
            </p>
          </div>
        </div>
      </div>

      {/* ESTADO GENERAL */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
              <CheckCircle2 size={22} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Estado de integraciones
              </h2>

              <p className="text-sm text-slate-500">
                Resumen parcial de las consultas de Discord, IA y preferencias.
              </p>
            </div>
          </div>

          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              aiLoading || discordLoading || notificationsLoading
                ? "bg-slate-100 text-slate-600"
                : aiError || discordError || notificationsError
                  ? "bg-amber-100 text-amber-800"
                  : "bg-green-100 text-green-700"
            }`}
          >
            {aiLoading || discordLoading || notificationsLoading
              ? "Consultando"
              : aiError || discordError || notificationsError
                ? "Requiere atención"
                : "Consultas correctas"}
          </span>
        </div>

        <p className="mt-4 text-xs text-slate-500">
          Este indicador no verifica la disponibilidad completa del sistema,
          la base de datos ni los servicios de Google Cloud.
        </p>
      </div>
      {/* CONFIGURACIÓN */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">

        {/* DISCORD */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600">
              <MessageSquare size={20} />
            </div>
            <div>
              <h2 className="font-semibold text-slate-900">Discord</h2>
              <p className="text-xs text-slate-400">Integración con la comunidad real</p>
            </div>
          </div>

          <div className="space-y-5">
            <div>
              <label className="text-sm font-medium text-slate-700">
                Servidor
              </label>
              <div className="mt-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800">
                CloudED
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">
                Canales disponibles
              </label>

              <select
                value={discordChannelId}
                onChange={(event) => setDiscordChannelId(event.target.value)}
                disabled={discordLoading || discordChannels.length === 0}
                className="mt-2 w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-orange-500 disabled:bg-slate-100"
              >
                {discordChannels.length === 0 && (
                  <option value="">
                    {discordLoading ? "Consultando canales..." : "Sin canales disponibles"}
                  </option>
                )}

                {discordChannels.map((canal) => (
                  <option key={canal.id} value={canal.id}>
                    #{canal.nombre}
                  </option>
                ))}
              </select>

              <p className="mt-2 text-xs text-slate-500">
                {discordChannels.length} canales recibidos desde el Motor IA.
              </p>
            </div>

            <div className="flex items-center justify-between rounded-lg bg-slate-50 p-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Consulta de canales
                </p>
                <p className="text-xs text-slate-400">
                  Estado de comunicación con el servicio de Discord
                </p>
              </div>

              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  discordLoading
                    ? "bg-slate-200 text-slate-700"
                    : discordError || discordChannels.length === 0
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-green-100 text-green-700"
                }`}
              >
                {discordLoading
                  ? "Consultando"
                  : discordError || discordChannels.length === 0
                    ? "No disponible"
                    : "Canales disponibles"}
              </span>
            </div>

            {discordError && (
              <p role="alert" className="text-sm text-red-600">
                {discordError}
              </p>
            )}

            <p className="text-xs text-slate-400">
              Consultar o seleccionar un canal no publica mensajes en Discord.
            </p>
          </div>
        </div>
        {/* IA */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-600">
              <Bot size={20} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Inteligencia artificial
              </h2>
              <p className="text-xs text-slate-400">
                Configuración efectiva del Motor IA
              </p>
            </div>
          </div>

          {aiLoading ? (
            <p className="text-sm text-slate-500">
              Consultando configuración del Motor IA...
            </p>
          ) : aiError ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4">
              <p className="text-sm font-medium text-red-700">
                No se pudo consultar la configuración IA
              </p>
              <p className="mt-1 break-words text-xs text-red-600">
                {aiError}
              </p>
            </div>
          ) : aiSettings ? (
            <div className="space-y-5">
              <div>
                <label className="text-sm font-medium text-slate-700">
                  Proveedor configurado
                </label>
                <div className="mt-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-800">
                  {aiSettings.provider}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700">
                  Modelo efectivo
                </label>
                <div className="mt-2 break-words rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800">
                  {aiSettings.model}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700">
                  Temperatura configurada
                </label>
                <div className="mt-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-800">
                  {aiSettings.temperature}
                </div>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-medium text-slate-700">
                  Estado del proveedor
                </p>

                <p className="mt-1 text-xs text-slate-600">
                  {aiSettings.provider_verified
                    ? "Proveedor verificado por el servicio."
                    : "Conectividad externa pendiente de verificar."}
                </p>

                <p className="mt-2 text-xs text-slate-500">
                  {aiSettings.description}
                </p>
              </div>

              <p className="text-xs text-slate-400">
                Configuración de solo lectura. Los cambios de modelo
                requieren una integración persistente y controlada.
              </p>
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              Configuración IA no disponible.
            </p>
          )}
        </div>
        {/* RAG */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
              <Database size={20} />
            </div>

            <div className="flex-1">
              <h2 className="font-semibold text-slate-900">
                Base de conocimiento
              </h2>
              <p className="text-xs text-slate-400">
                Recuperación de información y contexto institucional
              </p>
            </div>

            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              No configurado
            </span>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Sistema RAG
                </p>
                <p className="text-xs text-slate-400">
                  Recuperación aumentada por generación
                </p>
              </div>

              <span className="text-right text-xs font-medium text-slate-600">
                Sin implementación verificada
              </span>
            </div>

            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Documentos indexados
                </p>
                <p className="text-xs text-slate-400">
                  Cursos, FAQs y recursos institucionales
                </p>
              </div>

              <span className="text-sm font-semibold text-slate-600">
                No disponible
              </span>
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Base vectorial
                </p>
                <p className="text-xs text-slate-400">
                  Almacenamiento y consulta de embeddings
                </p>
              </div>

              <span className="text-right text-xs font-medium text-slate-600">
                No configurada
              </span>
            </div>
          </div>

          <p className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs leading-relaxed text-slate-500">
            No se identificó una integración RAG operativa en el código
            inspeccionado. Esta sección permanecerá informativa hasta
            implementar y verificar el servicio de conocimiento.
          </p>
        </div>
        {/* GOOGLE CLOUD PLATFORM */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
              <Cloud size={20} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Google Cloud Platform
              </h2>
              <p className="text-xs text-slate-400">
                Infraestructura y almacenamiento de CloudEdTech
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Imágenes corporativas
                </p>
                <p className="text-xs text-slate-400">
                  Persistencia de piezas generadas en Content Studio
                </p>
              </div>

              <span className="rounded-full bg-slate-100 px-3 py-1 text-right text-xs font-medium text-slate-600">
                Almacenamiento local
              </span>
            </div>

            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Reportes JSON
                </p>
                <p className="text-xs text-slate-400">
                  Google Cloud Storage
                </p>
              </div>

              <span className="rounded-full bg-amber-50 px-3 py-1 text-right text-xs font-medium text-amber-700">
                GCS sin configurar
              </span>
            </div>

            <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Base de datos administrativa
                </p>
                <p className="text-xs text-slate-400">
                  Usuarios, roles y auditoría
                </p>
              </div>

              <span className="text-right text-xs font-medium text-slate-600">
                Verificación pendiente
              </span>
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Persistencia del Motor IA
                </p>
                <p className="text-xs text-slate-400">
                  Datos y servicios de análisis
                </p>
              </div>

              <span className="text-right text-xs font-medium text-slate-600">
                Verificación pendiente
              </span>
            </div>
          </div>

          <p className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs leading-relaxed text-slate-500">
            Estados basados en la inspección local de configuración.
            No representan una comprobación de conectividad con Google Cloud.
            La reactivación de los recursos y la migración de almacenamiento
            se realizarán durante la fase de integración y despliegue.
          </p>
        </div>

      </div>
      {/* SEGURIDAD Y USUARIOS */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">

        {/* USUARIOS */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100 text-green-600">
              <Users size={20} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Usuarios y roles
              </h2>

              <p className="text-xs text-slate-400">
                Control de acceso al sistema
              </p>
            </div>
          </div>

          <div className="space-y-3">

            <div className="flex items-center justify-between rounded-lg bg-slate-50 p-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Administradores
                </p>
              </div>

              <span className="font-semibold text-slate-900">
                {users.filter((user) => user.role === "admin").length}
              </span>
            </div>

            <div className="flex items-center justify-between rounded-lg bg-slate-50 p-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Revisores
                </p>
              </div>

              <span className="font-semibold text-slate-900">
                {users.filter((user) => user.role === "reviewer").length}
              </span>
            </div>

            <div className="flex items-center justify-between rounded-lg bg-slate-50 p-4">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Community Managers
                </p>
              </div>

              <span className="font-semibold text-slate-900">
                {users.filter((user) => user.role === "community_manager").length}
              </span>
            </div>

          </div>
        </div>

        {/* SEGURIDAD */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-100 text-red-500">
              <ShieldCheck size={20} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Seguridad
              </h2>

              <p className="text-xs text-slate-400">
                Protección y autenticación
              </p>
            </div>
          </div>

          <div className="space-y-4">

            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Autenticación
                </p>

                <p className="text-xs text-slate-400">
                  Inicio de sesión protegido
                </p>
              </div>

              <span className="text-sm font-semibold text-green-600">
                Activa
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Registro de auditoría
                </p>

                <p className="text-xs text-slate-400">
                  Acciones administrativas
                </p>
              </div>

              <span className="text-sm font-semibold text-green-600">
                Activo
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Control de roles
                </p>

                <p className="text-xs text-slate-400">
                  Permisos por usuario
                </p>
              </div>

              <span className="text-sm font-semibold text-green-600">
                Activo
              </span>
            </div>

          </div>
        </div>

      </div>

      <CommunitySimulationSettings />

      {/* NOTIFICACIONES */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-yellow-100 text-yellow-600">
            <Bell size={20} />
          </div>

          <div>
            <h2 className="font-semibold text-slate-900">
              Notificaciones
            </h2>
            <p className="text-xs text-slate-400">
              Preferencias personales de alertas de CloudEdTech
            </p>
          </div>
        </div>

        <p className="mt-4 text-xs text-slate-500">
          Estas opciones guardan tus preferencias. La entrega automática
          de alertas todavía está pendiente de integración.
        </p>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          {(
            [
              ["highlights_enabled", "Nuevas historias destacadas"],
              ["sentiment_enabled", "Alertas de sentimiento"],
              ["approvals_enabled", "Contenido pendiente"],
            ] as const
          ).map(([campo, etiqueta]) => (
            <label
              key={campo}
              className="flex items-center gap-3 rounded-lg bg-slate-50 p-4"
            >
              <input
                type="checkbox"
                checked={notificationPreferences[campo]}
                disabled={notificationsLoading || notificationsSaving || Boolean(notificationsError)}
                onChange={(event) => {
                  const checked = event.target.checked;
                  setNotificationPreferences((actual) => ({
                    ...actual,
                    [campo]: checked,
                  }));
                  setNotificationsMessage(null);
                }}
                className="h-4 w-4 accent-orange-500 disabled:opacity-50"
              />

              <span className="text-sm text-slate-700">
                {etiqueta}
              </span>
            </label>
          ))}
        </div>

        {notificationsLoading && (
          <p className="mt-4 text-sm text-slate-500">
            Cargando preferencias...
          </p>
        )}

        {notificationsError && (
          <p role="alert" className="mt-4 text-sm text-red-600">
            {notificationsError}
          </p>
        )}

        {notificationsMessage && (
          <p role="status" className="mt-4 text-sm text-green-700">
            {notificationsMessage}
          </p>
        )}

        <div className="mt-5 flex justify-end">
          <button
            type="button"
            disabled={
              notificationsLoading ||
              notificationsSaving ||
              Boolean(notificationsError)
            }
            onClick={async () => {
              setNotificationsSaving(true);
              setNotificationsMessage(null);

              try {
                const guardadas = await saveNotificationPreferences(
                  notificationPreferences
                );
                setNotificationPreferences(guardadas);
                setNotificationsError(null);
                setNotificationsMessage(
                  "Preferencias guardadas correctamente."
                );
              } catch (error) {
                setNotificationsError(
                  error instanceof Error
                    ? error.message
                    : "No fue posible guardar las preferencias."
                );
              } finally {
                setNotificationsSaving(false);
              }
            }}
            className="flex items-center gap-2 rounded-lg bg-orange-500 px-5 py-3 text-sm font-semibold text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            <Save size={17} />
            {notificationsSaving
              ? "Guardando..."
              : "Guardar preferencias de notificaciones"}
          </button>
        </div>
      </div>

    </div>
  )
}

export default Settings