import { baseApi } from './baseApi';

export interface AnalyticsOverview {
    total_incidents: number;
    resolved: number;
    avg_resolution_time_minutes: number;
    sla_compliance_percentage: number;
    period_days: number;
}

export interface IncidentTrend {
    month: string;
    created: number;
    resolved: number;
}

export interface AlertBySeverity {
    severity: string;
    count: number;
    percentage: number;
}

export interface IncidentCategory {
    category: string;
    count: number;
    trend: number;
}

export interface TeamPerformance {
    team: string;
    avgResponse: string;
    avgResolution: string;
    slaCompliance: number;
}

export interface TopPerformer {
    name: string;
    resolved: number;
    avgTime: string;
    rating: number;
}

export interface AIMetrics {
    incidentsClassified: number;
    suggestionsAccepted: number;
    predictionsMade: number;
    preventedIncidents: number;
    accuracyRate: number;
    timeSaved: string;
}

export interface PlaybookStat {
    name: string;
    executions: number;
    successRate: number;
    avgDuration: string;
}

export const analyticsApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getAnalyticsOverview: builder.query<AnalyticsOverview, number | void>({
            query: (days = 30) => `/analytics/overview?days=${days}`,
        }),

        getIncidentTrends: builder.query<IncidentTrend[], number | void>({
            query: (months = 6) => `/analytics/incident-trends?months=${months}`,
        }),

        getAlertsBySeverity: builder.query<AlertBySeverity[], number | void>({
            query: (days = 30) => `/analytics/alerts-by-severity?days=${days}`,
        }),

        getTopIncidentCategories: builder.query<IncidentCategory[], { limit?: number; days?: number }>({
            query: ({ limit = 5, days = 30 } = {}) => `/analytics/top-incident-categories?limit=${limit}&days=${days}`,
        }),

        getTeamPerformance: builder.query<TeamPerformance[], number | void>({
            query: (days = 30) => `/analytics/team-performance?days=${days}`,
        }),

        getTopPerformers: builder.query<TopPerformer[], { limit?: number; days?: number }>({
            query: ({ limit = 5, days = 30 } = {}) => `/analytics/top-performers?limit=${limit}&days=${days}`,
        }),

        getAIMetrics: builder.query<AIMetrics, number | void>({
            query: (days = 30) => `/analytics/ai-metrics?days=${days}`,
        }),

        getPlaybookStats: builder.query<PlaybookStat[], { limit?: number; days?: number }>({
            query: ({ limit = 5, days = 30 } = {}) => `/analytics/playbook-stats?limit=${limit}&days=${days}`,
        }),
    }),
});

export const {
    useGetAnalyticsOverviewQuery,
    useGetIncidentTrendsQuery,
    useGetAlertsBySeverityQuery,
    useGetTopIncidentCategoriesQuery,
    useGetTeamPerformanceQuery,
    useGetTopPerformersQuery,
    useGetAIMetricsQuery,
    useGetPlaybookStatsQuery,
} = analyticsApi;
