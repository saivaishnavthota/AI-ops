import { baseApi } from './baseApi';

export interface Prediction {
    id: string;
    organization_id: string;
    type: string;
    resource: string;
    prediction: string;
    likelihood: number;
    impact: string;
    timeframe: string;
    predicted_date: string | null;
    status: string;
    recommended_action: string;
    details: string | null;
    prevention_steps: string[];
    action_taken: string | null;
    action_taken_at: string | null;
    action_taken_by_id: string | null;
    model_version: string | null;
    confidence_factors: Record<string, any>;
    created_at: string;
    updated_at: string;
}

export interface PredictionStats {
    total_predictions: number;
    active_predictions: number;
    prevented_count: number;
    occurred_count: number;
    expired_count: number;
    avg_likelihood: number;
    by_type: Record<string, number>;
    by_impact: Record<string, number>;
}

export interface PredictionCreateRequest {
    type: string;
    resource: string;
    prediction: string;
    likelihood: number;
    impact: string;
    timeframe: string;
    recommended_action: string;
    details?: string;
    prevention_steps?: string[];
}

export interface PredictionActionRequest {
    action_taken: string;
}

export const predictionsApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getPredictions: builder.query<{ items: Prediction[]; total: number }, { skip?: number; limit?: number; status?: string; type?: string; impact?: string }>({
            query: ({ skip = 0, limit = 100, status, type, impact }) => ({
                url: '/predictions',
                params: { skip, limit, status, type, impact },
            }),
            providesTags: ['Predictions'],
        }),
        getPredictionStats: builder.query<PredictionStats, void>({
            query: () => '/predictions/stats',
            providesTags: ['Predictions'],
        }),
        getPrediction: builder.query<Prediction, string>({
            query: (id) => `/predictions/${id}`,
            providesTags: (_result, _error, id) => [{ type: 'Predictions', id }],
        }),
        createPrediction: builder.mutation<Prediction, PredictionCreateRequest>({
            query: (data) => ({
                url: '/predictions',
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['Predictions'],
        }),
        takeActionOnPrediction: builder.mutation<Prediction, { id: string; data: PredictionActionRequest }>({
            query: ({ id, data }) => ({
                url: `/predictions/${id}/take-action`,
                method: 'POST',
                body: data,
            }),
            invalidatesTags: ['Predictions'],
        }),
        dismissPrediction: builder.mutation<Prediction, string>({
            query: (id) => ({
                url: `/predictions/${id}/dismiss`,
                method: 'POST',
            }),
            invalidatesTags: ['Predictions'],
        }),
        deletePrediction: builder.mutation<void, string>({
            query: (id) => ({
                url: `/predictions/${id}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['Predictions'],
        }),
    }),
});

export const {
    useGetPredictionsQuery,
    useGetPredictionStatsQuery,
    useGetPredictionQuery,
    useCreatePredictionMutation,
    useTakeActionOnPredictionMutation,
    useDismissPredictionMutation,
    useDeletePredictionMutation,
} = predictionsApi;
