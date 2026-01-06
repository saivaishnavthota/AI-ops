import { baseApi } from './baseApi';

export interface Investigation {
    id: string;
    organization_id: string;
    title: string;
    description: string;
    status: string;
    priority: string;
    assignee_id: string | null;
    assignee_name: string;
    progress: number;
    events_linked: number;
    findings: string[];
    timeline: Array<{ date: string; action: string; user: string }>;
    created_by_id: string | null;
    created_at: string;
    updated_at: string;
}

export interface InvestigationCreateRequest {
    title: string;
    description: string;
    priority: string;
    assignee_name: string;
}

export interface InvestigationUpdateRequest {
    title?: string;
    description?: string;
    status?: string;
    priority?: string;
    assignee_name?: string;
    progress?: number;
    findings?: string[];
    timeline?: Array<{ date: string; action: string; user: string }>;
}

export const investigationsApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getInvestigations: builder.query<{ items: Investigation[]; total: number }, { skip?: number; limit?: number; status?: string; priority?: string }>({
            query: ({ skip = 0, limit = 100, status, priority }) => ({
                url: '/investigations',
                params: { skip, limit, status, priority },
            }),
            providesTags: ['Investigations'],
        }),
        getInvestigation: builder.query<Investigation, string>({
            query: (id) => `/investigations/${id}`,
            providesTags: (_result, _error, id) => [{ type: 'Investigations', id }],
        }),
        createInvestigation: builder.mutation<Investigation, InvestigationCreateRequest>({
            query: (data) => ({
                url: '/investigations',
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['Investigations'],
        }),
        updateInvestigation: builder.mutation<Investigation, { id: string; data: InvestigationUpdateRequest }>({
            query: ({ id, data }) => ({
                url: `/investigations/${id}`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (_result, _error, { id }) => ['Investigations', { type: 'Investigations', id }],
        }),
        deleteInvestigation: builder.mutation<void, string>({
            query: (id) => ({
                url: `/investigations/${id}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['Investigations'],
        }),
    }),
});

export const {
    useGetInvestigationsQuery,
    useGetInvestigationQuery,
    useCreateInvestigationMutation,
    useUpdateInvestigationMutation,
    useDeleteInvestigationMutation,
} = investigationsApi;
