
import { useEffect, useState } from "react";
import { CloudUpload, RefreshCw, FileJson, Download, Eye, X, Trash2 } from "lucide-react";
import { listWeeklyReports, startWeeklySync, deleteWeeklyReport } from "../api/ociStorage";
import { getCurrentUser } from "../api/auth";
import type { WeeklyReport } from "../api/ociStorage";

export default function WeeklyReportsPanel() {
    const [reports, setReports] = useState<WeeklyReport[]>([]);
    const [loading, setLoading] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [filter, setFilter] = useState("all");
    const [preview, setPreview] = useState<WeeklyReport | null>(null);
    const [isAdmin, setIsAdmin] = useState(false);
    const [deletingWeek, setDeletingWeek] = useState("");
    const [confirmDelete, setConfirmDelete] = useState<WeeklyReport | null>(null);

    useEffect(() => {
        let active = true;

        getCurrentUser()
            .then((user) => {
                if (active) setIsAdmin(user.role === "admin");
            })
            .catch(() => {
                if (active) setIsAdmin(false);
            });

        return () => { active = false; };
    }, []);

    const refresh = async () => {
        setLoading(true);
        setError("");
        try {
            const result = await listWeeklyReports();
            setReports(Array.isArray(result.reports) ? result.reports : []);
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : "No fue posible consultar los reportes.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void refresh();
    }, []);

    const generate = async () => {
        setSyncing(true);
        setError("");
        setMessage("");
        try {
            const result = await startWeeklySync();
            setMessage(result.message);
            await refresh();
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : "No fue posible generar el reporte.");
        } finally {
            setSyncing(false);
        }
    };


    const removeReport = async () => {
        if (!confirmDelete || deletingWeek || !isAdmin) return;

        const semana = confirmDelete.semana;
        setDeletingWeek(semana);
        setError("");
        setMessage("");

        try {
            const result = await deleteWeeklyReport(semana);

            if (result.status !== "deleted") {
                throw new Error("El backend no confirmo la eliminacion.");
            }

            setConfirmDelete(null);
            await refresh();
            setMessage(`Reporte ${semana} eliminado correctamente.`);
        } catch (cause) {
            setError(
                cause instanceof Error
                    ? cause.message
                    : "No fue posible eliminar el reporte."
            );
        } finally {
            setDeletingWeek("");
        }
    };

    const downloadReport = (report: WeeklyReport) => {
        if (!report.reporte) {
            setError("El contenido completo del informe no esta disponible.");
            return;
        }

        const filename = report.nombre_archivo ?? `${report.semana}.json`;
        const content = JSON.stringify(report.reporte, null, 2);
        const blob = new Blob([content], {
            type: "application/json;charset=utf-8",
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    };

    const filtered = reports.filter((report) => {
        const status = report.storage_status ?? report.status ?? "saved_locally";
        if (filter === "all") return true;
        if (filter === "sent") return status === "synced";
        if (filter === "error") return status === "error";
        return status !== "synced" && status !== "error";
    });

    return (
        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 p-6">
                <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-orange-50 p-3 text-orange-500">
                        <FileJson size={22} />
                    </div>
                    <div>
                        <h3 className="font-bold text-slate-900">Reportes semanales del Motor IA</h3>
                        <p className="mt-1 text-sm text-slate-500">
                            Historial de reportes y estado del almacenamiento.
                        </p>
                    </div>
                </div>
                <div className="flex flex-wrap gap-2">
                    <button
                        type="button"
                        onClick={() => void refresh()}
                        disabled={loading}
                        className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 disabled:opacity-50"
                    >
                        <RefreshCw size={16} />
                        {loading ? "Consultando..." : "Actualizar"}
                    </button>
                    <button
                        type="button"
                        onClick={() => void generate()}
                        disabled={syncing}
                        className="inline-flex items-center gap-2 rounded-xl bg-orange-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
                    >
                        <CloudUpload size={16} />
                        {syncing ? "Generando..." : "Generar reporte semanal"}
                    </button>
                </div>
            </div>

            <div className="flex flex-wrap gap-2 px-6 pt-5">
                {[
                    ["all", "Todos"],
                    ["sent", "Enviados a Google Cloud"],
                    ["pending", "Guardados localmente"],
                    ["error", "Errores"],
                ].map(([value, label]) => (
                    <button
                        key={value}
                        type="button"
                        onClick={() => setFilter(value)}
                        className={`rounded-lg px-3 py-2 text-xs font-semibold ${
                            filter === value
                                ? "bg-[#080A27] text-white"
                                : "bg-slate-100 text-slate-600"
                        }`}
                    >
                        {label}
                    </button>
                ))}
            </div>

            {message && (
                <p role="status" className="mx-6 mt-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700">
                    {message}
                </p>
            )}
            {error && (
                <p role="alert" className="mx-6 mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">
                    {error}
                </p>
            )}

            <div className="overflow-x-auto p-6">
                <table className="w-full min-w-[650px] text-left">
                    <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                        <tr>
                            <th className="px-4 py-3">Semana</th>
                            <th className="px-4 py-3">Archivo</th>
                            <th className="px-4 py-3">Estado</th>
                            <th className="px-4 py-3">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filtered.map((report) => {
                            const status = report.storage_status ?? report.status ?? "saved_locally";
                            return (
                                <tr key={report.semana}>
                                    <td className="px-4 py-4 text-sm font-semibold text-slate-800">
                                        {report.semana}
                                    </td>
                                    <td className="px-4 py-4 text-xs text-slate-600">
                                        {report.nombre_archivo ?? report.archivo ?? `${report.semana}.json`}
                                    </td>
                                    <td className="px-4 py-4 text-xs text-slate-700">
                                        {status === "synced"
                                            ? "Sincronizado con Google Cloud"
                                            : status === "error"
                                                ? "Error"
                                                : "Guardado en almacenamiento del Motor IA"}
                                    </td>
                                    <td className="px-4 py-4">
                                        <div className="flex flex-wrap gap-2">
                                            <button
                                                type="button"
                                                disabled={!report.reporte}
                                                onClick={() => setPreview(report)}
                                                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 disabled:opacity-40"
                                            >
                                                <Eye size={14} />
                                                Ver informe
                                            </button>
                                            <button
                                                type="button"
                                                disabled={!report.reporte}
                                                onClick={() => downloadReport(report)}
                                                className="inline-flex items-center gap-1 rounded-lg bg-orange-500 px-3 py-2 text-xs font-semibold text-white disabled:opacity-40"
                                            >
                                                <Download size={14} />
                                                Descargar JSON
                                            </button>
                                            {isAdmin && (
                                                <button
                                                    type="button"
                                                    disabled={Boolean(deletingWeek)}
                                                    onClick={() => setConfirmDelete(report)}
                                                    className="inline-flex items-center gap-1 rounded-lg border border-red-200 px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 disabled:opacity-40"
                                                >
                                                    <Trash2 size={14} />
                                                    Eliminar reporte
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                        {!loading && filtered.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-4 py-10 text-center text-sm text-slate-500">
                                    No hay reportes para mostrar.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
            {confirmDelete && isAdmin && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4">
                    <div
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="confirm-delete-report-title"
                        className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl"
                    >
                        <h3
                            id="confirm-delete-report-title"
                            className="text-lg font-bold text-slate-900"
                        >
                            ?Eliminar reporte semanal?
                        </h3>
                        <p className="mt-3 text-sm text-slate-600">
                            Se solicitara eliminar el reporte
                            <strong className="ml-1 text-slate-900">
                                {confirmDelete.nombre_archivo ?? `${confirmDelete.semana}.json`}
                            </strong>
                            . Esta accion no se puede deshacer.
                        </p>
                        <div className="mt-6 flex justify-end gap-3">
                            <button
                                type="button"
                                disabled={Boolean(deletingWeek)}
                                onClick={() => setConfirmDelete(null)}
                                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 disabled:opacity-40"
                            >
                                Cancelar
                            </button>
                            <button
                                type="button"
                                disabled={Boolean(deletingWeek)}
                                onClick={() => void removeReport()}
                                className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-40"
                            >
                                <Trash2 size={16} />
                                {deletingWeek ? "Eliminando..." : "Confirmar eliminacion"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {preview && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4">
                    <div className="flex max-h-[90vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
                        <div className="flex items-center justify-between border-b border-slate-200 p-5">
                            <div>
                                <h3 className="font-bold text-slate-900">
                                    Informe {preview.semana}
                                </h3>
                                <p className="text-xs text-slate-500">
                                    Vista previa del JSON generado por el Motor IA
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={() => setPreview(null)}
                                aria-label="Cerrar vista previa"
                                className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
                            >
                                <X size={20} />
                            </button>
                        </div>
                        <pre className="overflow-auto bg-slate-950 p-6 text-xs leading-relaxed text-emerald-300">
                            {JSON.stringify(preview.reporte, null, 2)}
                        </pre>
                        <div className="flex justify-end gap-2 border-t border-slate-200 p-4">
                            <button
                                type="button"
                                onClick={() => setPreview(null)}
                                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold"
                            >
                                Cerrar
                            </button>
                            <button
                                type="button"
                                onClick={() => downloadReport(preview)}
                                className="rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white"
                            >
                                Descargar informe
                            </button>
                        </div>
                    </div>
                </div>
            )}

        </section>
    );
}
