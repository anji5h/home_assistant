#!/bin/bash
set -e

echo "Initializing PostgreSQL + TimescaleDB..."

RETENTION_DAYS="${TIMESCALE_RETENTION_DAYS:-3}"
COMPRESSION_DAYS="${TIMESCALE_COMPRESSION_DAYS:-1}"

echo "Retention: ${RETENTION_DAYS} days"
echo "Compression after: ${COMPRESSION_DAYS} days"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create table
CREATE TABLE IF NOT EXISTS environment (
    created_at  TIMESTAMPTZ       NOT NULL,
    sensor_id   INTEGER           NOT NULL,
    location    TEXT              NOT NULL,
    temperature NUMERIC(5,2)      NOT NULL,
    humidity    INTEGER           NOT NULL,
    pressure    INTEGER           NOT NULL,
    uv_index    INTEGER           NOT NULL
);

-- Create hypertable (1 hour chunks)
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM _timescaledb_catalog.hypertable
        WHERE table_name = 'environment'
    ) THEN
        PERFORM create_hypertable(
            'environment',
            'created_at',
            chunk_time_interval => INTERVAL '1 hour'
        );
    END IF;
END
\$\$;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_environment_sensor_time
    ON environment (sensor_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_environment_location_time
    ON environment (location, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_environment_time
    ON environment (created_at DESC);

-- Enable compression
ALTER TABLE environment
SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id'
);

-- Compression policy (env-driven)
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM timescaledb_information.jobs
        WHERE proc_name = 'policy_compression'
          AND hypertable_name = 'environment'
    ) THEN
        PERFORM add_compression_policy(
            'environment',
            make_interval(days => ${COMPRESSION_DAYS})
        );
    END IF;
END
\$\$;

-- Retention policy (env-driven)
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM timescaledb_information.jobs
        WHERE proc_name = 'policy_retention'
          AND hypertable_name = 'environment'
    ) THEN
        PERFORM add_retention_policy(
            'environment',
            make_interval(days => ${RETENTION_DAYS})
        );
    END IF;
END
\$\$;

EOSQL

echo "TimescaleDB initialization complete."