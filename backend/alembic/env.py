"""
Alembic environment configuration for async SQLAlchemy.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import settings and models
from app.config.settings import settings
from app.models.base import Base

# Import all models to ensure they're registered with Base.metadata
from app.models.organization import Organization
from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.incident import Incident, IncidentComment, IncidentTimeline
from app.models.alert import Alert, AlertCorrelation, AlertSource
from app.models.playbook import Playbook, PlaybookExecution, PlaybookStep
from app.models.prediction import Prediction
from app.models.security import SecurityEvent
from app.models.ticket import Ticket, KnowledgeBaseArticle
from app.models.investigation import Investigation
from app.models.audit import AuditLog

# Alembic Config object
config = context.config

# Override sqlalchemy.url with settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData object for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using sync engine."""
    from sqlalchemy import engine_from_config
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
