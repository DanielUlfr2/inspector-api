// src/features/history/historyService.ts
import apiClient from '../../api/apiClient';
import { GlobalStat } from '../../types/history';

const HISTORY_PATH = import.meta.env.VITE_API_DASHBOARD_HISTORY;

export const historyService = {
    /**
     * Formatea una fecha a 'YYYY-MM-DDTHH:mm:ss.sss' (sin la Z)
     * Esto asegura que el backend reciba la hora local exacta de tu PC.
     */
    /**
     * Formatea una fecha a 'YYYY-MM-DDTHH:mm:ss.sss' para Colombia
     */
    formatDateToLocalISO(date: Date): string {
        // Para enviar al backend, el backend debería recibir la fecha tal cual la genera el navegador
        // Pero si quieres asegurar que el backend reciba la hora local (no UTC):
        const offset = date.getTimezoneOffset() * 60000;
        const localISOTime = new Date(date.getTime() - offset).toISOString().slice(0, -1);
        return localISOTime;
    },

    /**
     * Obtiene el rango de fechas predeterminado (últimas 24 horas)
     */
    getDefaultRange() {
        const end = new Date();
        const start = new Date();
        start.setHours(start.getHours() - 24);

        return {
            start: this.formatDateToLocalISO(start),
            end: this.formatDateToLocalISO(end)
        };
    },

    /**
     * Obtiene el rango de fechas según las horas especificadas
     */
    getRangeByHours(hours: number) {
        const end = new Date();
        const start = new Date();
        start.setHours(start.getHours() - hours);

        return {
            start: this.formatDateToLocalISO(start),
            end: this.formatDateToLocalISO(end)
        };
    },

    /**
     * Formatea el timestamp para mostrar en la gráfica según el rango de tiempo
     */
    formatTimestamp(timestamp: string, hourRange: number): string {
        // Corrección de Bug: Si el backend envía "2025-12-28T18:25:00Z" (Fake UTC)
        // pero la hora REAL era 18:25, al parsearlo como UTC se resta -5h -> 13:25.
        // Solución: Quitamos la 'Z' para que se parsee como Hora Local (Server Time).
        const rawTimestamp = timestamp.endsWith('Z') ? timestamp.slice(0, -1) : timestamp;
        const date = new Date(rawTimestamp);

        // Forzamos la localización a Colombia 'es-CO' (UTC-5)
        const options: Intl.DateTimeFormatOptions = {
            timeZone: 'America/Bogota',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        };

        if (hourRange > 24) {
            options.day = '2-digit';
            options.month = '2-digit';
        }

        return new Intl.DateTimeFormat('es-CO', options).format(date);
    },

    /**
     * Calcula las horas entre dos fechas
     */
    getHoursBetween(startDate: string, endDate: string): number {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffMs = end.getTime() - start.getTime();
        return Math.round(diffMs / (1000 * 60 * 60));
    },

    /**
     * Obtiene las estadísticas globales en un rango de fechas
     * @param startDate Fecha de inicio (opcional)
     * @param endDate Fecha de fin (opcional)
     * @param fleetId ID de la flota para filtrar (opcional)
     */
    async getGlobalStats(startDate?: string, endDate?: string, fleetId?: string): Promise<GlobalStat[]> {
        const range = this.getDefaultRange();
        const start = startDate || range.start;
        const end = endDate || range.end;

        try {
            const response = await apiClient.get<{ stats: GlobalStat[] }>(`${HISTORY_PATH}/global-stats`, {
                params: {
                    start_date: start,
                    end_date: end,
                    ...(fleetId && { fleet_id: fleetId }) // Solo incluir si fleetId está definido
                }
            });

            const rawStats = response.data.stats || [];

            // Calcular el rango de horas para determinar el formato de fecha
            const hourRange = this.getHoursBetween(start, end);

            return rawStats.map(item => ({
                ...item,
                time: this.formatTimestamp(item.timestamp, hourRange)
            }));
        } catch (error) {
            console.error("Error en historyService:", error);
            return [];
        }
    }
};