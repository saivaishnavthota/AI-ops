"""add investigations table

Revision ID: 20260105_investigations
Revises: 20260105_security_tickets
Create Date: 2026-01-05 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260105_investigations'
down_revision = '20260105_security_tickets'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create investigations table
    op.create_table('investigations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assignee_name', sa.String(length=255), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('events_linked', sa.Integer(), nullable=True),
        sa.Column('findings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timeline', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investigations_organization_id'), 'investigations', ['organization_id'], unique=False)
    op.create_index(op.f('ix_investigations_status'), 'investigations', ['status'], unique=False)
    op.create_index(op.f('ix_investigations_priority'), 'investigations', ['priority'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_investigations_priority'), table_name='investigations')
    op.drop_index(op.f('ix_investigations_status'), table_name='investigations')
    op.drop_index(op.f('ix_investigations_organization_id'), table_name='investigations')
    op.drop_table('investigations')
