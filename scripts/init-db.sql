-- AI-Ops Platform Database Initialization Script
-- This script runs on first container startup

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for full-text search (will be used after tables are created by Alembic)
-- These are placeholder comments for reference

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE aiops_db TO aiops;

-- Create schema if needed (optional, using public schema by default)
-- CREATE SCHEMA IF NOT EXISTS aiops;
-- GRANT ALL ON SCHEMA aiops TO aiops;

-- Performance tuning for containerized environment
-- These would typically be in postgresql.conf but can be set per-session
-- ALTER SYSTEM SET shared_buffers = '256MB';
-- ALTER SYSTEM SET effective_cache_size = '768MB';
-- ALTER SYSTEM SET maintenance_work_mem = '64MB';
-- ALTER SYSTEM SET checkpoint_completion_target = 0.9;
-- ALTER SYSTEM SET wal_buffers = '7864kB';
-- ALTER SYSTEM SET default_statistics_target = 100;
-- ALTER SYSTEM SET random_page_cost = 1.1;
-- ALTER SYSTEM SET effective_io_concurrency = 200;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'AI-Ops Platform database initialized successfully';
END $$;
