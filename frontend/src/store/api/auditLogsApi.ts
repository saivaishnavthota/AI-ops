import { baseApi } from './baseApi';

export interface AuditLogEntry {
    id: string;
    organization_id: string;
    user_id: string | null;
    user_name: string | null;
    user_email: string | null;
    action: string;
    resource_type: string;
    resource_id: string;
    resource_name: string | null;
    description: string;
    changes: Record<string, { old: unknown; new: unknown }> | null;
    ip_address: string;
    user_agent: string;
    status: string;
    error_message: string | null;
    created_at: string;
}

export interface AuditLogStats {
    total_actions: number;
    actions_today: number;
    actions_this_week: number;
    by_action: Record<string, number>;
    by_resource_type: Record<string, number>;
    by_user: Array<{ user_id: string; count: number }>;
    recent_activity: AuditLogEntry[];
}

export const auditLogsApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getAuditLogs: builder.query<{ items: AuditLogEntry[]; total: number; page: number; page_size: number }, {
            page?: number;
            page_size?: number;
            action?: string;
            resource_type?: string;
            status?: string;
        }>({
            query: ({ page = 1, page_size = 50, action, resource_type, status }) => ({
                url: '/audit-logs',
                params: { page, page_size, action, resource_type, status },
            }),
            providesTags: ['AuditLogs'],
        }),
        getAuditLogStats: builder.query<AuditLogStats, void>({
            query: () => '/audit-logs/stats',
            providesTags: ['AuditLogs'],
        }),
        getAuditLog: builder.query<AuditLogEntry, string>({
            query: (id) => `/audit-logs/${id}`,
            providesTags: (_result, _error, id) => [{ type: 'AuditLogs', id }],
        }),
    }),
});

export const {
    useGetAuditLogsQuery,
    useGetAuditLogStatsQuery,
    useGetAuditLogQuery,
} = auditLogsApi;
