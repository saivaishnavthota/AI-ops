import { baseApi } from './baseApi';

export interface Playbook {
    id: string;
    organization_id: string;
    name: string;
    description: string | null;
    trigger_conditions: Record<string, any>;
    steps: Array<Record<string, any>>;
    requires_approval: boolean;
    approval_roles: string[];
    is_active: boolean;
    execution_count: number;
    success_count: number;
    failure_count: number;
    success_rate: number;
    avg_execution_time_seconds: number | null;
    tags: string[];
    created_by_id: string | null;
    created_at: string;
    updated_at: string;
}

export interface PlaybookExecution {
    id: string;
    playbook_id: string;
    organization_id: string;
    incident_id: string | null;
    alert_id: string | null;
    status: string;
    triggered_by: string | null;
    triggered_by_user_id: string | null;
    approval_required: boolean;
    approved_by_id: string | null;
    approved_at: string | null;
    approval_comment: string | null;
    execution_log: Array<any>;
    result: Record<string, any> | null;
    current_step: number;
    error_message: string | null;
    started_at: string | null;
    completed_at: string | null;
    duration_seconds: number;
    created_at: string;
    playbook_name?: string;
    triggered_by_user_name?: string;
    approved_by_name?: string;
}

export interface PlaybookCreateRequest {
    name: string;
    description?: string;
    trigger_conditions?: Record<string, any>;
    steps: Array<Record<string, any>>;
    requires_approval?: boolean;
    approval_roles?: string[];
    tags?: string[];
}

export interface PlaybookUpdateRequest {
    name?: string;
    description?: string;
    trigger_conditions?: Record<string, any>;
    steps?: Array<Record<string, any>>;
    requires_approval?: boolean;
    approval_roles?: string[];
    is_active?: boolean;
    tags?: string[];
}

export interface PlaybookExecuteRequest {
    incident_id?: string;
    alert_id?: string;
    parameters?: Record<string, any>;
}

export const playbooksApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getPlaybooks: builder.query<{ items: Playbook[]; total: number }, { skip?: number; limit?: number; status?: string }>({
            query: ({ skip = 0, limit = 100, status }) => ({
                url: '/playbooks',
                params: { skip, limit, status },
            }),
            providesTags: ['Playbooks'],
        }),
        getPlaybook: builder.query<Playbook, string>({
            query: (id) => `/playbooks/${id}`,
            providesTags: (_result, _error, id) => [{ type: 'Playbooks', id }],
        }),
        createPlaybook: builder.mutation<Playbook, PlaybookCreateRequest>({
            query: (data) => ({
                url: '/playbooks',
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['Playbooks'],
        }),
        updatePlaybook: builder.mutation<Playbook, { id: string; data: PlaybookUpdateRequest }>({
            query: ({ id, data }) => ({
                url: `/playbooks/${id}`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (_result, _error, { id }) => ['Playbooks', { type: 'Playbooks', id }],
        }),
        deletePlaybook: builder.mutation<void, string>({
            query: (id) => ({
                url: `/playbooks/${id}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['Playbooks'],
        }),
        executePlaybook: builder.mutation<PlaybookExecution, { id: string; data: PlaybookExecuteRequest }>({
            query: ({ id, data }) => ({
                url: `/playbooks/${id}/execute`,
                method: 'POST',
                body: data,
            }),
            invalidatesTags: (_result, _error, { id }) => ['Playbooks', { type: 'Playbooks', id }],
        }),
        getPlaybookExecutions: builder.query<{ items: PlaybookExecution[]; total: number }, { id: string; skip?: number; limit?: number }>({
            query: ({ id, skip = 0, limit = 50 }) => ({
                url: `/playbooks/${id}/executions`,
                params: { skip, limit },
            }),
        }),
    }),
});

export const {
    useGetPlaybooksQuery,
    useGetPlaybookQuery,
    useCreatePlaybookMutation,
    useUpdatePlaybookMutation,
    useDeletePlaybookMutation,
    useExecutePlaybookMutation,
    useGetPlaybookExecutionsQuery,
} = playbooksApi;
