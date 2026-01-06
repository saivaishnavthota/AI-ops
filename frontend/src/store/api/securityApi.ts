import { baseApi } from './baseApi';

export interface SecurityEvent {
    id: string;
    organization_id: string;
    type: string;
    severity: string;
    source: string;
    description: string;
    status: string;
    affected_asset: string | null;
    ip_address: string | null;
    user: string | null;
    details: string | null;
    resolved_at: string | null;
    resolved_by_id: string | null;
    resolution_notes: string | null;
    created_at: string;
    updated_at: string;
}

export interface SecurityEventStats {
    total_events: number;
    critical_count: number;
    high_count: number;
    open_count: number;
    by_severity: Record<string, number>;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
}

export interface SecurityEventCreateRequest {
    type: string;
    severity: string;
    source: string;
    description: string;
    affected_asset?: string;
    ip_address?: string;
    user?: string;
    details?: string;
}

export interface SecurityEventUpdateRequest {
    status?: string;
    resolution_notes?: string;
}

export const securityApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getSecurityEvents: builder.query<{ items: SecurityEvent[]; total: number }, { skip?: number; limit?: number; severity?: string; status?: string }>({
            query: ({ skip = 0, limit = 100, severity, status }) => ({
                url: '/security-events',
                params: { skip, limit, severity, status },
            }),
            providesTags: ['SecurityEvents'],
        }),
        getSecurityEventStats: builder.query<SecurityEventStats, void>({
            query: () => '/security-events/stats',
            providesTags: ['SecurityEvents'],
        }),
        getSecurityEvent: builder.query<SecurityEvent, string>({
            query: (id) => `/security-events/${id}`,
            providesTags: (_result, _error, id) => [{ type: 'SecurityEvents', id }],
        }),
        createSecurityEvent: builder.mutation<SecurityEvent, SecurityEventCreateRequest>({
            query: (data) => ({
                url: '/security-events',
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['SecurityEvents'],
        }),
        updateSecurityEvent: builder.mutation<SecurityEvent, { id: string; data: SecurityEventUpdateRequest }>({
            query: ({ id, data }) => ({
                url: `/security-events/${id}`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: ['SecurityEvents'],
        }),
        deleteSecurityEvent: builder.mutation<void, string>({
            query: (id) => ({
                url: `/security-events/${id}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['SecurityEvents'],
        }),
    }),
});

export const {
    useGetSecurityEventsQuery,
    useGetSecurityEventStatsQuery,
    useGetSecurityEventQuery,
    useCreateSecurityEventMutation,
    useUpdateSecurityEventMutation,
    useDeleteSecurityEventMutation,
} = securityApi;
