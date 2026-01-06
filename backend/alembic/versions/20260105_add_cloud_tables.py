"""add cloud tables

Revision ID: 20260105_cloud
Revises: 
Create Date: 2026-01-05 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260105_cloud'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cloud_resources table
    op.create_table('cloud_resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('running', 'stopped', 'pending', 'error', name='resourcestatus'), nullable=False),
        sa.Column('instance_type', sa.String(length=100), nullable=True),
        sa.Column('cpu_usage', sa.Float(), nullable=True),
        sa.Column('memory_usage', sa.Float(), nullable=True),
        sa.Column('private_ip', sa.String(length=50), nullable=True),
        sa.Column('public_ip', sa.String(length=50), nullable=True),
        sa.Column('monthly_cost', sa.Float(), nullable=True),
        sa.Column('launch_time', sa.DateTime(), nullable=True),
        sa.Column('resource_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cloud_resources_organization_id'), 'cloud_resources', ['organization_id'], unique=False)

    # Create cloud_cost_items table
    op.create_table('cloud_cost_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('service', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('current_month', sa.Float(), nullable=True),
        sa.Column('last_month', sa.Float(), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['cloud_resources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cloud_cost_items_organization_id'), 'cloud_cost_items', ['organization_id'], unique=False)

    # Create cloud_optimization_recommendations table
    op.create_table('cloud_optimization_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('recommendation_type', sa.String(length=100), nullable=False),
        sa.Column('resource_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=False),
        sa.Column('impact', sa.Enum('high', 'medium', 'low', name='recommendationimpact'), nullable=False),
        sa.Column('monthly_savings', sa.Float(), nullable=True),
        sa.Column('effort', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('pending', 'applied', 'dismissed', name='recommendationstatus'), nullable=False),
        sa.Column('ai_confidence', sa.Float(), nullable=True),
        sa.Column('implementation_steps', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['cloud_resources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cloud_optimization_recommendations_organization_id'), 'cloud_optimization_recommendations', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_cloud_optimization_recommendations_organization_id'), table_name='cloud_optimization_recommendations')
    op.drop_table('cloud_optimization_recommendations')
    op.drop_index(op.f('ix_cloud_cost_items_organization_id'), table_name='cloud_cost_items')
    op.drop_table('cloud_cost_items')
    op.drop_index(op.f('ix_cloud_resources_organization_id'), table_name='cloud_resources')
    op.drop_table('cloud_resources')
    op.execute('DROP TYPE IF EXISTS resourcestatus')
    op.execute('DROP TYPE IF EXISTS recommendationimpact')
    op.execute('DROP TYPE IF EXISTS recommendationstatus')
