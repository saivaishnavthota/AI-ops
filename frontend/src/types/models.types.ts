// User types
export interface User {
  id: string;
  organization_id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  full_name: string;
  role: string;
  phone: string | null;
  job_title: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  mfa_enabled: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
  preferences?: Record<string, unknown>;
  permissions?: string[];
}

// Organization types
export interface Organization {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  subscription_tier: string;
  settings: Record<string, unknown>;
  features: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Team types
export interface Team {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  team_type: string;
  settings: Record<string, unknown>;
  is_active: boolean;
  member_count: number;
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  id: string;
  team_id: string;
  user_id: string;
  role: string;
  is_on_call: boolean;
  notifications_enabled: boolean;
  created_at: string;
  user_email?: string;
  user_name?: string;
}

// Incident types
export type IncidentStatus = 'open' | 'acknowledged' | 'in_progress' | 'resolved' | 'closed';
export type IncidentPriority = 'p1' | 'p2' | 'p3' | 'p4' | 'p5';
export type IncidentSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface Incident {
  id: string;
  organization_id: string;
  incident_number: string;
  title: string;
  description: string | null;
  status: IncidentStatus;
  priority: IncidentPriority;
  severity: IncidentSeverity;
  impact: string | null;
  urgency: string | null;
  category: string | null;
  subcategory: string | null;
  assigned_team_id: string | null;
  assigned_user_id: string | null;
  reported_by_id: string | null;
  affected_services: string[];
  business_impact_score: number | null;
  ai_classification: Record<string, unknown> | null;
  ai_suggested_resolution: string | null;
  ai_confidence_score: number | null;
  root_cause: string | null;
  resolution_notes: string | null;
  is_predicted: boolean;
  tags: string[];
  metadata: Record<string, unknown>;
  acknowledged_at: string | null;
  resolved_at: string | null;
  closed_at: string | null;
  sla_breach_at: string | null;
  created_at: string;
  updated_at: string;
  assigned_team_name?: string;
  assigned_user_name?: string;
  reported_by_name?: string;
}

export interface IncidentComment {
  id: string;
  incident_id: string;
  user_id: string | null;
  content: string;
  is_internal: boolean;
  is_ai_generated: boolean;
  attachments: Array<{ name: string; url: string; type: string; size: number }>;
  created_at: string;
  user_name?: string;
  user_email?: string;
}

export interface IncidentTimeline {
  id: string;
  incident_id: string;
  user_id: string | null;
  event_type: string;
  description: string | null;
  changes: Record<string, { old: unknown; new: unknown }> | null;
  is_automated: boolean;
  created_at: string;
  user_name?: string;
}

export interface IncidentStatistics {
  total: number;
  open: number;
  acknowledged: number;
  in_progress: number;
  resolved: number;
  closed: number;
  by_priority: Record<string, number>;
  by_severity: Record<string, number>;
  by_category: Record<string, number>;
  avg_resolution_time_hours: number | null;
  mttr_hours: number | null;
}

// Alert types
export type AlertStatus = 'firing' | 'acknowledged' | 'resolved' | 'suppressed';
export type AlertSeverity = 'critical' | 'warning' | 'info';

export interface Alert {
  id: string;
  organization_id: string;
  alert_id_external: string | null;
  source: string;
  source_type: string | null;
  title: string | null;
  message: string | null;
  severity: AlertSeverity;
  status: AlertStatus;
  host: string | null;
  service: string | null;
  metric_name: string | null;
  metric_value: number | null;
  threshold_value: number | null;
  tags: Record<string, unknown>;
  correlation_id: string | null;
  incident_id: string | null;
  is_suppressed: boolean;
  suppression_reason: string | null;
  ai_correlation_score: number | null;
  fingerprint: string | null;
  occurrence_count: number;
  first_occurrence_at: string | null;
  last_occurrence_at: string | null;
  acknowledged_at: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertStatistics {
  total: number;
  firing: number;
  acknowledged: number;
  resolved: number;
  suppressed: number;
  by_severity: Record<string, number>;
  by_source: Record<string, number>;
  by_service: Record<string, number>;
}

// Paginated response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// API response types
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface MessageResponse {
  message: string;
  success: boolean;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}
