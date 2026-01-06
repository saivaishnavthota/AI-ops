import { baseApi } from './baseApi';

export interface Ticket {
    id: string;
    organization_id: string;
    subject: string;
    description: string;
    status: string;
    priority: string;
    category: string;
    requester_id: string | null;
    requester_name: string;
    assignee_id: string | null;
    assignee_name: string | null;
    comments: Array<{ user: string; text: string; time: string }>;
    resolved_at: string | null;
    created_at: string;
    updated_at: string;
}

export interface TicketCreateRequest {
    subject: string;
    description: string;
    priority: string;
    category: string;
    assignee_name?: string;
}

export interface TicketUpdateRequest {
    status?: string;
    assignee_id?: string;
    assignee_name?: string;
    comments?: Array<{ user: string; text: string; time: string }>;
}

export interface TicketAssignRequest {
    assignee_id: string;
}

export interface TicketResolveRequest {
    title?: string;
    content?: string;
    tags?: string[];
}

export interface KnowledgeBaseArticle {
    id: string;
    organization_id: string;
    title: string;
    excerpt: string;
    content: string;
    category: string;
    tags: string[];
    views: number;
    helpful_count: number;
    author_id: string | null;
    is_published: boolean;
    created_at: string;
    updated_at: string;
}

export interface KBArticleCreateRequest {
    title: string;
    excerpt: string;
    content: string;
    category: string;
    tags: string[];
}

export interface KBArticleUpdateRequest {
    title?: string;
    excerpt?: string;
    content?: string;
    category?: string;
    tags?: string[];
    is_published?: boolean;
}

export const ticketsApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getTickets: builder.query<{ items: Ticket[]; total: number }, { skip?: number; limit?: number; status?: string; priority?: string }>({
            query: ({ skip = 0, limit = 100, status, priority }) => ({
                url: '/tickets',
                params: { skip, limit, status, priority },
            }),
            providesTags: ['Tickets'],
        }),
        getTicket: builder.query<Ticket, string>({
            query: (id) => `/tickets/${id}`,
            providesTags: (_result, _error, id) => [{ type: 'Tickets', id }],
        }),
        createTicket: builder.mutation<Ticket, TicketCreateRequest>({
            query: (data) => ({
                url: '/tickets',
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['Tickets'],
        }),
        updateTicket: builder.mutation<Ticket, { id: string; data: TicketUpdateRequest }>({
            query: ({ id, data }) => ({
                url: `/tickets/${id}`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (_result, _error, { id }) => ['Tickets', { type: 'Tickets', id }],
        }),
        assignTicket: builder.mutation<Ticket, { id: string; data: TicketAssignRequest }>({
            query: ({ id, data }) => ({
                url: `/tickets/${id}/assign`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (_result, _error, { id }) => ['Tickets', { type: 'Tickets', id }],
        }),
        resolveTicketWithFeedback: builder.mutation<Ticket, { id: string; feedback: TicketResolveRequest }>({
            query: ({ id, feedback }) => ({
                url: `/tickets/${id}/resolve`,
                method: 'PUT',
                body: feedback,
            }),
            invalidatesTags: (_result, _error, { id }) => ['Tickets', { type: 'Tickets', id }, 'KBArticles'],
        }),
        deleteTicket: builder.mutation<void, string>({
            query: (id) => ({
                url: `/tickets/${id}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['Tickets'],
        }),
        getKBArticles: builder.query<{ items: KnowledgeBaseArticle[]; total: number }, { skip?: number; limit?: number; category?: string; search?: string }>({
            query: ({ skip = 0, limit = 100, category, search }) => ({
                url: '/knowledge-base',
                params: { skip, limit, category, search },
            }),
            providesTags: ['KBArticles'],
        }),
        getKBArticle: builder.query<KnowledgeBaseArticle, string>({
            query: (id) => `/knowledge-base/${id}`,
            providesTags: (_result, _error, id) => [{ type: 'KBArticles', id }],
        }),
        createKBArticle: builder.mutation<KnowledgeBaseArticle, KBArticleCreateRequest>({
            query: (data) => ({
                url: '/knowledge-base',
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['KBArticles'],
        }),
        updateKBArticle: builder.mutation<KnowledgeBaseArticle, { id: string; data: KBArticleUpdateRequest }>({
            query: ({ id, data }) => ({
                url: `/knowledge-base/${id}`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (_result, _error, { id }) => ['KBArticles', { type: 'KBArticles', id }],
        }),
        markKBArticleHelpful: builder.mutation<KnowledgeBaseArticle, string>({
            query: (id) => ({
                url: `/knowledge-base/${id}/helpful`,
                method: 'POST',
            }),
            invalidatesTags: (_result, _error, id) => [{ type: 'KBArticles', id }],
        }),
        deleteKBArticle: builder.mutation<void, string>({
            query: (id) => ({
                url: `/knowledge-base/${id}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['KBArticles'],
        }),
    }),
});

export const {
    useGetTicketsQuery,
    useGetTicketQuery,
    useCreateTicketMutation,
    useUpdateTicketMutation,
    useAssignTicketMutation,
    useResolveTicketWithFeedbackMutation,
    useDeleteTicketMutation,
    useGetKBArticlesQuery,
    useGetKBArticleQuery,
    useCreateKBArticleMutation,
    useUpdateKBArticleMutation,
    useMarkKBArticleHelpfulMutation,
    useDeleteKBArticleMutation,
} = ticketsApi;
