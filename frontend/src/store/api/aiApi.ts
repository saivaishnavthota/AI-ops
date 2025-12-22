import { baseApi } from './baseApi';

// Types
export interface AIStatus {
  enabled: boolean;
  classification_enabled: boolean;
  suggestion_enabled: boolean;
  correlation_enabled: boolean;
  model: string;
  confidence_threshold: number;
}

export interface Classification {
  category: string;
  subcategory: string;
  suggested_priority: string;
  suggested_severity: string;
  confidence: number;
  reasoning: string;
  keywords: string[];
  affected_components: string[];
}

export interface ClassificationResponse {
  incident_id: string;
  classification: Classification;
  updated: boolean;
}

export interface Suggestion {
  summary: string;
  steps: string[];
  estimated_time: string;
  risk_level: string;
  requires_approval: boolean;
  automation_possible: boolean;
  related_runbooks: string[];
  confidence: number;
}

export interface SuggestionResponse {
  incident_id: string;
  suggestion: Suggestion;
  suggestion_text: string;
  updated: boolean;
}

export interface AnalysisResponse {
  incident_id: string;
  classification: Classification;
  suggestion: Suggestion;
  suggestion_text: string;
  updated: boolean;
}

export interface CorrelationGroup {
  alert_ids: string[];
  root_cause_id: string | null;
  correlation_type: string;
  confidence: number;
  reasoning: string;
  suggested_incident_title: string;
  suggested_incident_priority: string;
}

export interface Correlation {
  groups: CorrelationGroup[];
  uncorrelated_ids: string[];
  total_alerts: number;
  analysis_summary: string;
}

export interface CorrelationResponse {
  organization_id: string;
  correlation: Correlation;
  time_window_minutes: number;
}

export interface ClassifyTextRequest {
  title: string;
  description?: string;
  affected_services?: string[];
  tags?: string[];
}

export interface SuggestTextRequest {
  title: string;
  description?: string;
  category?: string;
  subcategory?: string;
  severity?: string;
  priority?: string;
  affected_services?: string[];
}

export const aiApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    // Get AI status
    getAIStatus: builder.query<AIStatus, void>({
      query: () => '/ai/status',
    }),

    // Classify an incident
    classifyIncident: builder.mutation<ClassificationResponse, { incidentId: string; updateIncident?: boolean }>({
      query: ({ incidentId, updateIncident = true }) => ({
        url: `/ai/incidents/${incidentId}/classify`,
        method: 'POST',
        body: { update_incident: updateIncident },
      }),
      invalidatesTags: (result, error, { incidentId }) => [{ type: 'Incident', id: incidentId }],
    }),

    // Get resolution suggestions for an incident
    suggestResolution: builder.mutation<SuggestionResponse, { incidentId: string; updateIncident?: boolean }>({
      query: ({ incidentId, updateIncident = true }) => ({
        url: `/ai/incidents/${incidentId}/suggest`,
        method: 'POST',
        body: { update_incident: updateIncident },
      }),
      invalidatesTags: (result, error, { incidentId }) => [{ type: 'Incident', id: incidentId }],
    }),

    // Full analysis (classify + suggest)
    analyzeIncident: builder.mutation<AnalysisResponse, { incidentId: string; updateIncident?: boolean }>({
      query: ({ incidentId, updateIncident = true }) => ({
        url: `/ai/incidents/${incidentId}/analyze`,
        method: 'POST',
        body: { update_incident: updateIncident },
      }),
      invalidatesTags: (result, error, { incidentId }) => [{ type: 'Incident', id: incidentId }],
    }),

    // Async analysis (queued)
    analyzeIncidentAsync: builder.mutation<{ message: string; incident_id: string; task_id: string }, string>({
      query: (incidentId) => ({
        url: `/ai/incidents/${incidentId}/analyze-async`,
        method: 'POST',
      }),
    }),

    // Correlate alerts
    correlateAlerts: builder.mutation<CorrelationResponse, { timeWindowMinutes?: number; statusFilter?: string[] }>({
      query: ({ timeWindowMinutes = 30, statusFilter }) => ({
        url: '/ai/alerts/correlate',
        method: 'POST',
        body: { time_window_minutes: timeWindowMinutes, status_filter: statusFilter },
      }),
    }),

    // Async correlation (queued)
    correlateAlertsAsync: builder.mutation<{ message: string; organization_id: string; task_id: string }, { timeWindowMinutes?: number }>({
      query: ({ timeWindowMinutes = 30 }) => ({
        url: '/ai/alerts/correlate-async',
        method: 'POST',
        body: { time_window_minutes: timeWindowMinutes },
      }),
    }),

    // Classify text (preview without incident)
    classifyText: builder.mutation<Classification, ClassifyTextRequest>({
      query: (body) => ({
        url: '/ai/classify',
        method: 'POST',
        body,
      }),
    }),

    // Suggest resolution for text (preview without incident)
    suggestText: builder.mutation<{ suggestion: Suggestion; suggestion_text: string }, SuggestTextRequest>({
      query: (body) => ({
        url: '/ai/suggest',
        method: 'POST',
        body,
      }),
    }),
  }),
});

export const {
  useGetAIStatusQuery,
  useClassifyIncidentMutation,
  useSuggestResolutionMutation,
  useAnalyzeIncidentMutation,
  useAnalyzeIncidentAsyncMutation,
  useCorrelateAlertsMutation,
  useCorrelateAlertsAsyncMutation,
  useClassifyTextMutation,
  useSuggestTextMutation,
} = aiApi;
