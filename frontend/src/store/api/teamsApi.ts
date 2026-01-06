import { baseApi } from './baseApi';

export interface TeamMember {
    id: string;
    user_id: string;
    name: string;
    email: string;
    role: string;
    is_on_call: boolean;
}

export interface Team {
    id: string;
    organization_id: string;
    name: string;
    description: string | null;
    team_type: string;
    member_count: number;
    on_call_person: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface TeamCreateRequest {
    name: string;
    description?: string;
    team_type: string;
}

export interface TeamUpdateRequest {
    name?: string;
    description?: string;
    team_type?: string;
}

export interface TeamMemberCreateRequest {
    user_id: string;
    role?: string;
    is_on_call?: boolean;
}

export interface TeamMemberUpdateRequest {
    role?: string;
    is_on_call?: boolean;
}

export const teamsApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getTeams: builder.query<{ items: Team[]; total: number }, { skip?: number; limit?: number }>({
            query: ({ skip = 0, limit = 100 }) => ({
                url: '/teams',
                params: { skip, limit },
            }),
            providesTags: ['Teams'],
        }),
        getTeam: builder.query<Team, string>({
            query: (id) => `/teams/${id}`,
            providesTags: (_result, _error, id) => [{ type: 'Teams', id }],
        }),
        createTeam: builder.mutation<Team, TeamCreateRequest>({
            query: (data) => ({
                url: '/teams',
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['Teams'],
        }),
        updateTeam: builder.mutation<Team, { id: string; data: TeamUpdateRequest }>({
            query: ({ id, data }) => ({
                url: `/teams/${id}`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (_result, _error, { id }) => ['Teams', { type: 'Teams', id }],
        }),
        deleteTeam: builder.mutation<void, string>({
            query: (id) => ({
                url: `/teams/${id}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['Teams'],
        }),
        getTeamMembers: builder.query<{ items: TeamMember[] }, string>({
            query: (teamId) => `/teams/${teamId}/members`,
            providesTags: (_result, _error, teamId) => [{ type: 'Teams', id: teamId }],
        }),
        addTeamMember: builder.mutation<TeamMember, { teamId: string; data: TeamMemberCreateRequest }>({
            query: ({ teamId, data }) => ({
                url: `/teams/${teamId}/members`,
                method: 'POST',
                body: data,
            }),
            invalidatesTags: (_result, _error, { teamId }) => ['Teams', { type: 'Teams', id: teamId }],
        }),
        updateTeamMember: builder.mutation<TeamMember, { teamId: string; memberId: string; data: TeamMemberUpdateRequest }>({
            query: ({ teamId, memberId, data }) => ({
                url: `/teams/${teamId}/members/${memberId}`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (_result, _error, { teamId }) => ['Teams', { type: 'Teams', id: teamId }],
        }),
        removeTeamMember: builder.mutation<void, { teamId: string; memberId: string }>({
            query: ({ teamId, memberId }) => ({
                url: `/teams/${teamId}/members/${memberId}`,
                method: 'DELETE',
            }),
            invalidatesTags: (_result, _error, { teamId }) => ['Teams', { type: 'Teams', id: teamId }],
        }),
    }),
});

export const {
    useGetTeamsQuery,
    useGetTeamQuery,
    useCreateTeamMutation,
    useUpdateTeamMutation,
    useDeleteTeamMutation,
    useGetTeamMembersQuery,
    useAddTeamMemberMutation,
    useUpdateTeamMemberMutation,
    useRemoveTeamMemberMutation,
} = teamsApi;
