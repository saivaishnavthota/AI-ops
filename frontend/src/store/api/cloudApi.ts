import { baseApi } from './baseApi';

export interface CloudResource {
    id: string;
    name: string;
    type: string;
    provider: string;
    region: string;
    status: 'running' | 'stopped' | 'pending' | 'error';
    cpu: number;
    memory: number;
    cost: number;
    instanceType?: string;
    privateIp?: string;
    publicIp?: string;
    launchTime?: string;
}

export interface CloudCostItem {
    id: string;
    service: string;
    category: string;
    currentMonth: number;
    lastMonth: number;
    change: number;
    budget: number;
    details?: Array<{
        resource: string;
        cost: number;
        usage: string;
    }>;
}

export interface OptimizationRecommendation {
    id: string;
    type: string;
    resource: string;
    description: string;
    impact: 'high' | 'medium' | 'low';
    savings: number;
    effort: string;
    status: 'pending' | 'applied' | 'dismissed';
    aiConfidence: number;
    steps?: string[];
}

export const cloudApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        listCloudResources: builder.query<CloudResource[], void>({
            query: () => '/cloud/resources',
            providesTags: ['CloudResource'],
        }),

        listCloudCosts: builder.query<CloudCostItem[], void>({
            query: () => '/cloud/costs',
            providesTags: ['CloudCost'],
        }),

        listOptimizationRecommendations: builder.query<OptimizationRecommendation[], void>({
            query: () => '/cloud/optimization-recommendations',
            providesTags: ['CloudOptimization'],
        }),

        applyOptimizationRecommendation: builder.mutation<{ message: string; savings: number }, string>({
            query: (id) => ({
                url: `/cloud/optimization-recommendations/${id}/apply`,
                method: 'POST',
            }),
            invalidatesTags: ['CloudOptimization', 'CloudCost'],
        }),

        dismissOptimizationRecommendation: builder.mutation<{ message: string }, string>({
            query: (id) => ({
                url: `/cloud/optimization-recommendations/${id}/dismiss`,
                method: 'POST',
            }),
            invalidatesTags: ['CloudOptimization'],
        }),

        startCloudResource: builder.mutation<{ message: string }, string>({
            query: (id) => ({
                url: `/cloud/resources/${id}/start`,
                method: 'POST',
            }),
            invalidatesTags: ['CloudResource'],
        }),

        stopCloudResource: builder.mutation<{ message: string }, string>({
            query: (id) => ({
                url: `/cloud/resources/${id}/stop`,
                method: 'POST',
            }),
            invalidatesTags: ['CloudResource'],
        }),

        rebootCloudResource: builder.mutation<{ message: string }, string>({
            query: (id) => ({
                url: `/cloud/resources/${id}/reboot`,
                method: 'POST',
            }),
            invalidatesTags: ['CloudResource'],
        }),
    }),
});

export const {
    useListCloudResourcesQuery,
    useListCloudCostsQuery,
    useListOptimizationRecommendationsQuery,
    useApplyOptimizationRecommendationMutation,
    useDismissOptimizationRecommendationMutation,
    useStartCloudResourceMutation,
    useStopCloudResourceMutation,
    useRebootCloudResourceMutation,
} = cloudApi;
