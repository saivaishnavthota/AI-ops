"""add alert management tables

Revision ID: alert_management_001
Revises: 
Create Date: 2026-01-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'alert_management_001'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Alert Correlation Rules
    op.create_table(
        'alert_correlation_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('criteria', postgresql.JSON, nullable=False),
        sa.Column('use_ai_correlation', sa.Boolean, default=True),
        sa.Column('similarity_threshold', sa.Float, default=0.8),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('priority', sa.Integer, default=1),
        sa.Column('correlation_count', sa.Integer, default=0),
        sa.Column('last_triggered', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Alert Suppression Rules
    op.create_table(
        'alert_suppression_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('criteria', postgresql.JSON, nullable=False),
        sa.Column('suppression_duration', sa.Integer, nullable=False),
        sa.Column('max_occurrences', sa.Integer, default=1),
        sa.Column('schedule', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('suppressed_count', sa.Integer, default=0),
        sa.Column('last_triggered', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Alert Webhook Endpoints
    op.create_table(
        'alert_webhook_endpoints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('endpoint_url', sa.String(500), nullable=False, unique=True),
        sa.Column('secret_token', sa.String(255), nullable=True),
        sa.Column('source_type', sa.String(100), nullable=False),
        sa.Column('source_config', postgresql.JSON, nullable=True),
        sa.Column('field_mapping', postgresql.JSON, nullable=True),
        sa.Column('filters', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('alerts_received', sa.Integer, default=0),
        sa.Column('last_alert_received', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Alert Deduplications
    op.create_table(
        'alert_deduplications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('primary_alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alerts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('duplicate_alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alerts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('similarity_score', sa.Float, nullable=False),
        sa.Column('deduplication_method', sa.String(100), nullable=False),
        sa.Column('deduplication_criteria', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Alert to Incident Conversions
    op.create_table(
        'alert_incident_conversions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alerts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('conversion_method', sa.String(100), nullable=False),
        sa.Column('conversion_rule_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('converted_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('conversion_context', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Update alerts table with new fields
    op.add_column('alerts', sa.Column('description', sa.Text, nullable=True))
    op.add_column('alerts', sa.Column('environment', sa.String(100), nullable=True, index=True))
    op.add_column('alerts', sa.Column('external_id', sa.String(255), nullable=True, index=True))
    op.add_column('alerts', sa.Column('raw_data', postgresql.JSON, nullable=True))
    op.add_column('alerts', sa.Column('first_occurrence', sa.DateTime(timezone=True), nullable=True))
    op.add_column('alerts', sa.Column('last_occurrence', sa.DateTime(timezone=True), nullable=True))
    op.add_column('alerts', sa.Column('resolved_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))

    # Update alert_correlations table
    op.add_column('alert_correlations', sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True))
    op.add_column('alert_correlations', sa.Column('related_alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alerts.id', ondelete='CASCADE'), nullable=True, index=True))


def downgrade():
    # Drop new tables
    op.drop_table('alert_incident_conversions')
    op.drop_table('alert_deduplications')
    op.drop_table('alert_webhook_endpoints')
    op.drop_table('alert_suppression_rules')
    op.drop_table('alert_correlation_rules')

    # Remove new columns from alerts
    op.drop_column('alerts', 'resolved_by_id')
    op.drop_column('alerts', 'last_occurrence')
    op.drop_column('alerts', 'first_occurrence')
    op.drop_column('alerts', 'raw_data')
    op.drop_column('alerts', 'external_id')
    op.drop_column('alerts', 'environment')
    op.drop_column('alerts', 'description')

    # Remove new columns from alert_correlations
    op.drop_column('alert_correlations', 'related_alert_id')
    op.drop_column('alert_correlations', 'organization_id')
