"""add predictions table

Revision ID: 20260105_predictions
Revises: 20260105_cloud
Create Date: 2026-01-05 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260105_predictions'
down_revision = '20260105_cloud'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create predictions table
    op.create_table('predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('resource', sa.String(length=255), nullable=False),
        sa.Column('prediction', sa.Text(), nullable=False),
        sa.Column('likelihood', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('impact', sa.String(length=20), nullable=False),
        sa.Column('timeframe', sa.String(length=100), nullable=False),
        sa.Column('predicted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('recommended_action', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('prevention_steps', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('action_taken', sa.String(length=255), nullable=True),
        sa.Column('action_taken_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('action_taken_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('confidence_factors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['action_taken_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_organization_id'), 'predictions', ['organization_id'], unique=False)
    op.create_index(op.f('ix_predictions_type'), 'predictions', ['type'], unique=False)
    op.create_index(op.f('ix_predictions_impact'), 'predictions', ['impact'], unique=False)
    op.create_index(op.f('ix_predictions_status'), 'predictions', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_predictions_status'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_impact'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_type'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_organization_id'), table_name='predictions')
    op.drop_table('predictions')
