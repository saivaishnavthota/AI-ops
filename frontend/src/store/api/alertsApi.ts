import { baseApi } from './baseApi';
import type { Alert, AlertStatistics, Incident, PaginatedResponse } from '../../types/models.types';

interface ListAlertsParams {
  page?: number;
  page_size?: number;
  status?: string[];
  severity?: string[];
  source?: string;
  host?: string;
  service?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

interface CreateAlertRequest {
  alert_id_external?: string;
  source: string;
  source_type?: string;
  title: string;
  message?: string;
  severity?: string;
  host?: string;
  service?: string;
  metric_name?: string;
  metric_value?: number;
  threshold_value?: number;
  tags?: Record<string, unknown>;
  raw_payload?: Record<string, unknown>;
}

interface SuppressAlertRequest {
  reason: string;
  duration_hours?: number;
}

interface CreateIncidentFromAlertRequest {
  title?: string;
  description?: string;
  priority?: string;
  severity?: string;
  assigned_team_id?: string;
}

interface AlertSource {
  id: string;
  organization_id: string;
  name: string;
  source_type: string;
  config: Record<string, unknown>;
  is_active: boolean;
  last_received_at: string | null;
  total_alerts_received: number;
  created_at: string;
  updated_at: string;
  webhook_url?: string;
}

interface CreateAlertSourceRequest {
  name: string;
  source_type: string;
  config?: Record<string, unknown>;
}

export const alertsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    listAlerts: builder.query<PaginatedResponse<Alert>, ListAlertsParams>({
      query: (params) => ({
        url: '/alerts',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.items.map(({ id }) => ({ type: 'Alert' as const, id })),
              { type: 'Alert', id: 'LIST' },
            ]
          : [{ type: 'Alert', id: 'LIST' }],
    }),

    getAlert: builder.query<Alert, string>({
      query: (id) => `/alerts/${id}`,
      providesTags: (result, error, id) => [{ type: 'Alert', id }],
    }),

    ingestAlert: builder.mutation<Alert, CreateAlertRequest>({
      query: (data) => ({
        url: '/alerts',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Alert', id: 'LIST' }],
    }),

    acknowledgeAlert: builder.mutation<Alert, string>({
      query: (id) => ({
        url: `/alerts/${id}/acknowledge`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Alert', id },
        { type: 'Alert', id: 'LIST' },
      ],
    }),

    resolveAlert: builder.mutation<Alert, string>({
      query: (id) => ({
        url: `/alerts/${id}/resolve`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Alert', id },
        { type: 'Alert', id: 'LIST' },
      ],
    }),

    suppressAlert: builder.mutation<Alert, { id: string; data: SuppressAlertRequest }>({
      query: ({ id, data }) => ({
        url: `/alerts/${id}/suppress`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Alert', id },
        { type: 'Alert', id: 'LIST' },
      ],
    }),

    createIncidentFromAlert: builder.mutation<Incident, { id: string; data: CreateIncidentFromAlertRequest }>({
      query: ({ id, data }) => ({
        url: `/alerts/${id}/create-incident`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Alert', id },
        { type: 'Alert', id: 'LIST' },
        { type: 'Incident', id: 'LIST' },
      ],
    }),

    getAlertStatistics: builder.query<AlertStatistics, void>({
      query: () => '/alerts/statistics',
    }),

    listAlertSources: builder.query<AlertSource[], void>({
      query: () => '/alerts/sources',
    }),

    createAlertSource: builder.mutation<AlertSource, CreateAlertSourceRequest>({
      query: (data) => ({
        url: '/alerts/sources',
        method: 'POST',
        body: data,
      }),
    }),
  }),
});

export const {
  useListAlertsQuery,
  useGetAlertQuery,
  useIngestAlertMutation,
  useAcknowledgeAlertMutation,
  useResolveAlertMutation,
  useSuppressAlertMutation,
  useCreateIncidentFromAlertMutation,
  useGetAlertStatisticsQuery,
  useListAlertSourcesQuery,
  useCreateAlertSourceMutation,
} = alertsApi;
