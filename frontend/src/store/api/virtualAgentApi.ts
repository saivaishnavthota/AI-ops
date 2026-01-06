import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQuery } from './baseApi';

export interface StartConversationRequest {
    subject: string;
    initial_message: string;
    user_email?: string;
}

export interface SendMessageRequest {
    conversation_id: string;
    message: string;
}

export interface Message {
    id: string;
    type: 'user' | 'agent' | 'system';
    content: string;
    sender_name?: string;
    timestamp: string;
    ai_confidence?: number;
    kb_articles?: string[];
    actions?: string[];
}

export interface Conversation {
    id: string;
    subject: string;
    status: string;
    user_name: string;
    intent?: string;
    sentiment?: string;
    category?: string;
    priority?: string;
    created_at: string;
    updated_at: string;
}

export interface ChatResponse {
    response: string;
    confidence: number;
    intent: string;
    sentiment: string;
    category: string;
    priority: string;
    kb_articles: string[];
    actions_executed: string[];
    escalated: boolean;
    response_time_ms: number;
}

export interface AgentScore {
    agent_id: string;
    agent_name: string;
    score: number;
    reasoning: string;
    availability: string;
    current_workload: number;
    skill_match: number;
    performance_score: number;
}

export interface RoutingRecommendation {
    recommended_agent?: AgentScore;
    alternative_agents: AgentScore[];
    team_recommendation?: string;
    escalation_needed: boolean;
    reasoning: string;
    confidence: number;
}

export interface TrendAnalysis {
    trend_type: string;
    category: string;
    description: string;
    confidence: number;
    impact_score: number;
    recommended_actions: string[];
    affected_users: number;
    time_period: string;
}

export interface AnomalyDetection {
    anomaly_type: string;
    description: string;
    severity: string;
    affected_area: string;
    detection_time: string;
    confidence: number;
    suggested_investigation: string[];
}

export interface ProactiveRecommendation {
    recommendation_id: string;
    type: string;
    title: string;
    description: string;
    priority: string;
    target_audience: string[];
    estimated_impact: string;
    implementation_effort: string;
    success_metrics: string[];
}

export interface AgentPerformance {
    agent_id: string;
    agent_name: string;
    avg_resolution_time_minutes: number;
    avg_satisfaction: number;
    avg_fcr_rate: number;
    total_tickets: number;
    total_conversations: number;
}

export interface VirtualAgentStatus {
    status: string;
    last_24h_stats: {
        total_conversations: number;
        auto_resolved: number;
        auto_resolution_rate: number;
        avg_confidence: number;
    };
    ai_enabled: boolean;
    features: {
        intent_recognition: boolean;
        smart_routing: boolean;
        proactive_support: boolean;
        knowledge_integration: boolean;
    };
}

export const virtualAgentApi = createApi({
    reducerPath: 'virtualAgentApi',
    baseQuery,
    tagTypes: ['Conversation', 'Message', 'Analytics', 'Performance'],
    endpoints: (builder) => ({
        // Virtual Agent Chat Endpoints
        startConversation: builder.mutation<
            { conversation_id: string; subject: string; status: string; messages: Message[] },
            StartConversationRequest
        >({
            query: (data) => ({
                url: '/virtual-agent/conversations',
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['Conversation'],
        }),

        sendMessage: builder.mutation<ChatResponse, SendMessageRequest>({
            query: ({ conversation_id, message }) => ({
                url: `/virtual-agent/conversations/${conversation_id}/messages`,
                method: 'POST',
                body: { message },
            }),
            invalidatesTags: ['Message'],
        }),

        getConversationMessages: builder.query<Message[], { conversation_id: string; limit?: number }>({
            query: ({ conversation_id, limit = 50 }) => ({
                url: `/virtual-agent/conversations/${conversation_id}/messages`,
                params: { limit },
            }),
            providesTags: ['Message'],
        }),

        getConversations: builder.query<Conversation[], { status?: string; limit?: number }>({
            query: ({ status, limit = 50 } = {}) => ({
                url: '/virtual-agent/conversations',
                params: { status, limit },
            }),
            providesTags: ['Conversation'],
        }),

        // Smart Routing Endpoints
        getTicketRouting: builder.mutation<RoutingRecommendation, { ticket_id: string; priority_override?: string }>({
            query: ({ ticket_id, priority_override }) => ({
                url: `/virtual-agent/routing/tickets/${ticket_id}`,
                method: 'POST',
                body: priority_override ? { priority_override } : {},
            }),
        }),

        getConversationRouting: builder.mutation<RoutingRecommendation, { conversation_id: string }>({
            query: ({ conversation_id }) => ({
                url: `/virtual-agent/routing/conversations/${conversation_id}`,
                method: 'POST',
            }),
        }),

        assignTicket: builder.mutation<{ success: boolean; message: string }, { ticket_id: string; agent_id: string }>({
            query: ({ ticket_id, agent_id }) => ({
                url: `/virtual-agent/routing/assign/${ticket_id}`,
                method: 'POST',
                body: { agent_id },
            }),
            invalidatesTags: ['Analytics'],
        }),

        // Analytics Endpoints
        getSupportTrends: builder.query<TrendAnalysis[], { days_back?: number }>({
            query: ({ days_back = 30 } = {}) => ({
                url: '/virtual-agent/analytics/trends',
                params: { days_back },
            }),
            providesTags: ['Analytics'],
        }),

        getAnomalies: builder.query<AnomalyDetection[], { hours_back?: number }>({
            query: ({ hours_back = 24 } = {}) => ({
                url: '/virtual-agent/analytics/anomalies',
                params: { hours_back },
            }),
            providesTags: ['Analytics'],
        }),

        getProactiveRecommendations: builder.query<ProactiveRecommendation[], void>({
            query: () => '/virtual-agent/analytics/recommendations',
            providesTags: ['Analytics'],
        }),

        getKnowledgeGaps: builder.query<any[], { days_back?: number }>({
            query: ({ days_back = 30 } = {}) => ({
                url: '/virtual-agent/analytics/knowledge-gaps',
                params: { days_back },
            }),
            providesTags: ['Analytics'],
        }),

        // Performance Endpoints
        getAgentPerformance: builder.query<AgentPerformance[], { days_back?: number }>({
            query: ({ days_back = 30 } = {}) => ({
                url: '/virtual-agent/performance/agents',
                params: { days_back },
            }),
            providesTags: ['Performance'],
        }),

        getVirtualAgentStatus: builder.query<VirtualAgentStatus, void>({
            query: () => '/virtual-agent/status',
            providesTags: ['Analytics'],
        }),
    }),
});

export const {
    // Chat mutations
    useStartConversationMutation,
    useSendMessageMutation,

    // Chat queries
    useGetConversationMessagesQuery,
    useGetConversationsQuery,

    // Routing mutations
    useGetTicketRoutingMutation,
    useGetConversationRoutingMutation,
    useAssignTicketMutation,

    // Analytics queries
    useGetSupportTrendsQuery,
    useGetAnomaliesQuery,
    useGetProactiveRecommendationsQuery,
    useGetKnowledgeGapsQuery,

    // Performance queries
    useGetAgentPerformanceQuery,
    useGetVirtualAgentStatusQuery,
} = virtualAgentApi;