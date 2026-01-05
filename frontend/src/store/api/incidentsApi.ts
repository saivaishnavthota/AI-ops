import { baseApi } from './baseApi';
import type {
  Incident,
  IncidentComment,
  IncidentTimeline,
  IncidentStatistics,
  PaginatedResponse,
} from '../../types/models.types';

interface ListIncidentsParams {
  page?: number;
  page_size?: number;
  status?: string[];
  priority?: string[];
  severity?: string[];
  assigned_team_id?: string;
  assigned_user_id?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  _refresh?: number; // Cache buster parameter (backend ignores it)
}

interface CreateIncidentRequest {
  title: string;
  description?: string;
  priority?: string;
  severity?: string;
  impact?: string;
  urgency?: string;
  category?: string;
  subcategory?: string;
  assigned_team_id?: string;
  assigned_user_id?: string;
  affected_services?: string[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

interface UpdateIncidentRequest extends Partial<CreateIncidentRequest> {
  status?: string;
  root_cause?: string;
  resolution_notes?: string;
}

interface ResolveIncidentRequest {
  resolution_notes: string;
  root_cause?: string;
}

interface AssignIncidentRequest {
  assigned_team_id?: string;
  assigned_user_id?: string;
  comment?: string;
}

interface AddCommentRequest {
  content: string;
  is_internal?: boolean;
  attachments?: Array<{ name: string; url: string; type: string; size: number }>;
}

export const incidentsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    listIncidents: builder.query<PaginatedResponse<Incident>, ListIncidentsParams>({
      query: (params) => ({
        url: '/incidents',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.items.map(({ id }) => ({ type: 'Incident' as const, id })),
              { type: 'Incident', id: 'LIST' },
            ]
          : [{ type: 'Incident', id: 'LIST' }],
    }),

    getIncident: builder.query<Incident & { comments: IncidentComment[]; timeline: IncidentTimeline[] }, string>({
      query: (id) => `/incidents/${id}`,
      providesTags: (result, error, id) => [{ type: 'Incident', id }],
    }),

    createIncident: builder.mutation<Incident, CreateIncidentRequest>({
      query: (data) => ({
        url: '/incidents',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Incident', id: 'LIST' }],
    }),

    updateIncident: builder.mutation<Incident, { id: string; data: UpdateIncidentRequest }>({
      query: ({ id, data }) => ({
        url: `/incidents/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Incident', id },
        { type: 'Incident', id: 'LIST' },
      ],
    }),

    acknowledgeIncident: builder.mutation<Incident, string>({
      query: (id) => ({
        url: `/incidents/${id}/acknowledge`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Incident', id },
        { type: 'Incident', id: 'LIST' },
      ],
    }),

    resolveIncident: builder.mutation<Incident, { id: string; data: ResolveIncidentRequest }>({
      query: ({ id, data }) => ({
        url: `/incidents/${id}/resolve`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Incident', id },
        { type: 'Incident', id: 'LIST' },
      ],
    }),

    closeIncident: builder.mutation<Incident, string>({
      query: (id) => ({
        url: `/incidents/${id}/close`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Incident', id },
        { type: 'Incident', id: 'LIST' },
      ],
    }),

    assignIncident: builder.mutation<Incident, { id: string; data: AssignIncidentRequest }>({
      query: ({ id, data }) => ({
        url: `/incidents/${id}/assign`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Incident', id },
        { type: 'Incident', id: 'LIST' },
      ],
    }),

    getIncidentTimeline: builder.query<IncidentTimeline[], string>({
      query: (id) => `/incidents/${id}/timeline`,
    }),

    getIncidentComments: builder.query<IncidentComment[], string>({
      query: (id) => `/incidents/${id}/comments`,
    }),

    addIncidentComment: builder.mutation<IncidentComment, { id: string; data: AddCommentRequest }>({
      query: ({ id, data }) => ({
        url: `/incidents/${id}/comments`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Incident', id }],
    }),

    getIncidentStatistics: builder.query<IncidentStatistics, void>({
      query: () => '/incidents/statistics',
    }),
  }),
});

export const {
  useListIncidentsQuery,
  useGetIncidentQuery,
  useCreateIncidentMutation,
  useUpdateIncidentMutation,
  useAcknowledgeIncidentMutation,
  useResolveIncidentMutation,
  useCloseIncidentMutation,
  useAssignIncidentMutation,
  useGetIncidentTimelineQuery,
  useGetIncidentCommentsQuery,
  useAddIncidentCommentMutation,
  useGetIncidentStatisticsQuery,
} = incidentsApi;
