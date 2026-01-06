"""add security and tickets tables

Revision ID: 20260105_security_tickets
Revises: 20260105_predictions
Create Date: 2026-01-05 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260105_security_tickets'
down_revision = '20260105_predictions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create security_events table
    op.create_table('security_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('affected_asset', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user', sa.String(length=255), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_security_events_organization_id'), 'security_events', ['organization_id'], unique=False)
    op.create_index(op.f('ix_security_events_severity'), 'security_events', ['severity'], unique=False)
    op.create_index(op.f('ix_security_events_status'), 'security_events', ['status'], unique=False)

    # Create tickets table
    op.create_table('tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('requester_name', sa.String(length=255), nullable=False),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assignee_name', sa.String(length=255), nullable=True),
        sa.Column('comments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tickets_organization_id'), 'tickets', ['organization_id'], unique=False)
    op.create_index(op.f('ix_tickets_status'), 'tickets', ['status'], unique=False)
    op.create_index(op.f('ix_tickets_priority'), 'tickets', ['priority'], unique=False)

    # Create kb_articles table
    op.create_table('kb_articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('views', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('helpful_count', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_published', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kb_articles_organization_id'), 'kb_articles', ['organization_id'], unique=False)
    op.create_index(op.f('ix_kb_articles_category'), 'kb_articles', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_kb_articles_category'), table_name='kb_articles')
    op.drop_index(op.f('ix_kb_articles_organization_id'), table_name='kb_articles')
    op.drop_table('kb_articles')
    op.drop_index(op.f('ix_tickets_priority'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_status'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_organization_id'), table_name='tickets')
    op.drop_table('tickets')
    op.drop_index(op.f('ix_security_events_status'), table_name='security_events')
    op.drop_index(op.f('ix_security_events_severity'), table_name='security_events')
    op.drop_index(op.f('ix_security_events_organization_id'), table_name='security_events')
    op.drop_table('security_events')
