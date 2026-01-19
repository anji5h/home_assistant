# Home Assistant Sensor Data Ingestion System

A production-quality sensor data ingestion pipeline using PostgreSQL + TimescaleDB, designed for long-running endurance testing on resource-constrained systems (Raspberry Pi / 4GB RAM).

## Overview

This system migrates from InfluxDB v2 to PostgreSQL + TimescaleDB to address unbounded memory growth issues and provide stable, predictable resource usage for continuous sensor data ingestion.

### Key Features

- **Stable Memory Usage**: Bounded memory consumption, avoiding InfluxDB-style unbounded growth
- **Three Workload Profiles**: LOW, MEDIUM, HIGH for different testing scenarios
- **Concurrent Writers**: Supports multiple concurrent ingestion threads
- **Automatic Compression**: Compresses old data (>7 days) automatically
- **Retention Policy**: Automatically drops data older than 90 days
- **Home Assistant Compatible**: Sensor data structure compatible with Home Assistant

## Architecture

- **Database**: PostgreSQL 16 + TimescaleDB extension
- **API Framework**: FastAPI with async/await
- **Database Driver**: asyncpg (async PostgreSQL driver)
- **Scheduler**: APScheduler with async support
- **Containerization**: Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- 4GB+ RAM (for Raspberry Pi deployments)

### Setup

1. **Clone the repository**

2. **Create `.env` file**:
   ```bash
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_DATABASE=home_assistant
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   WORKLOAD=LOW
   WRITE_INTERVAL=1
   READ_INTERVAL=20
   TIMESCALE_RETENTION_HOURS=72
   TIMESCALE_COMPRESSION_HOURS=6
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Verify health**:
   ```bash
   curl http://localhost:8000/health
   ```

5. **Check database statistics**:
   ```bash
   docker exec -it home-assistant-postgres psql -U postgres -d home_assistant -c "SELECT * FROM get_environment_stats();"
   ```

## Workload Profiles

### LOW Workload
- **Inserts/sec**: 25
- **Writers**: 1
- **Sensors**: 10,000
- **Target CPU**: 20-40%
- **Use Case**: Background/idle ingestion, baseline testing

### MEDIUM Workload
- **Inserts/sec**: 100
- **Writers**: 2 concurrent
- **Sensors**: 25,000
- **Target CPU**: 50-70%
- **Use Case**: Sustained real-world load

### HIGH Workload
- **Inserts/sec**: 750 (500-1000 range)
- **Writers**: 5 concurrent (4-6 range)
- **Sensors**: 50,000
- **Target CPU**: 90-100%
- **Use Case**: Stress/endurance testing

## Database Schema

### Table: `environment`

```sql
CREATE TABLE environment (
    created_at TIMESTAMPTZ NOT NULL,
    sensor_id INTEGER NOT NULL,
    location TEXT NOT NULL,
    temperature NUMERIC(5, 2) NOT NULL,
    humidity INTEGER NOT NULL,
    pressure INTEGER NOT NULL,
    uv_index INTEGER NOT NULL
);
```

### TimescaleDB Features

- **Hypertable**: Automatic chunking with 1-hour intervals
- **Compression**: Automatic compression of chunks older than 7 days
- **Retention**: Automatic deletion of data older than 90 days
- **Indexes**: Optimized for time-series queries

## API Endpoints

### GET `/health`

Returns system health and workload information:

```json
{
  "status": "running",
  "workload": "LOW",
  "points_per_sec": 25,
  "num_writers": 1,
  "num_sensors": 10000
}
```

## Monitoring

### Database Statistics

```sql
SELECT * FROM get_environment_stats();
```

Returns:
- Total rows
- Oldest/newest timestamps
- Unique sensor count
- Unique location count

### Chunk Information

```sql
SELECT * FROM timescaledb_information.chunks 
WHERE hypertable_name = 'environment';
```

### Compression Status

```sql
SELECT * FROM timescaledb_information.jobs 
WHERE hypertable_name = 'environment';
```

### Disk Usage Estimation

```sql
SELECT * FROM estimate_disk_usage();
```

Returns:
- Table size (data)
- Indexes size
- Total size
- Estimated days of data

### Adjusting Retention Period

If you need to change the retention period (e.g., if disk space is tight):

```sql
-- Remove existing retention policy
SELECT remove_retention_policy('environment');

-- Add new retention policy (e.g., 7 days)
SELECT add_retention_policy('environment', INTERVAL '7 days');
```

**Note**: Shorter retention = less disk usage but less historical data.

## Performance Characteristics

### Memory Usage

- **PostgreSQL Base**: ~512MB (`shared_buffers`)
- **LOW Workload**: ~600MB total
- **MEDIUM Workload**: ~800MB total
- **HIGH Workload**: ~1.2GB total

Memory usage is **predictable and bounded**, unlike InfluxDB.

### CPU Usage

- Scales linearly with workload profile
- LOW: 20-40%
- MEDIUM: 50-70%
- HIGH: 90-100%

### Disk Usage

- **Uncompressed**: ~50 bytes per row
- **Compressed** (>7 days): ~5 bytes per row (90% compression)
- **14-day retention**: Optimized for 29GB disk space
  - HIGH workload: ~25GB for 14 days (leaves ~4GB for PostgreSQL overhead)
  - MEDIUM workload: ~4GB for 14 days
  - LOW workload: ~1GB for 14 days
- **Automatic deletion**: Data older than 14 days is automatically dropped

## Why PostgreSQL + TimescaleDB?

### InfluxDB Issues

1. **Unbounded Memory Growth**: TSM can accumulate unbounded memory
2. **Limited Resource Control**: Fewer knobs for memory management
3. **Unpredictable Performance**: Memory usage grows with data volume

### PostgreSQL + TimescaleDB Advantages

1. **Bounded Memory**: Fixed `shared_buffers`, connection pool limits
2. **Predictable Resource Usage**: Explicit limits, no unbounded growth
3. **Better for Edge Devices**: Runs reliably on 4GB RAM Raspberry Pi
4. **SQL Compatibility**: Standard SQL queries
5. **Automatic Optimization**: Compression and retention policies

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `postgres` | PostgreSQL hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_DATABASE` | `home_assistant` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `WORKLOAD` | `LOW` | Workload profile (LOW/MEDIUM/HIGH) |
| `WRITE_INTERVAL` | `1` | Write job interval (seconds) |
| `READ_INTERVAL` | `20` | Read job interval (seconds) |
| `TIMESCALE_RETENTION_HOURS` | `2` | TimeScale DB retention hours |
| `TIMESCALE_COMPRESSION_HOURS` | `10` | TimeScale DB compression hours |

## Development

### Project Structure

```
.
├── app/
│   ├── config.py          # Configuration settings
│   ├── postgres.py        # PostgreSQL service
│   ├── simulator.py        # Sensor data simulator
│   ├── scheduler.py       # Background job scheduler
│   ├── workload.py         # Workload profiles
│   ├── main.py            # FastAPI application
│   └── lifespan.py        # Application lifecycle
├── compose.yml            # Docker Compose configuration
├── init.sh               # Database initialization script
├── requirements.txt       # Python dependencies
```

### Running Locally

  ```bash
   docker compose up -d --build 
  ```

## Troubleshooting

### High Memory Usage

1. Reduce `shared_buffers` in `compose.yml`
2. Reduce connection pool size
3. Check for long-running queries
4. Verify compression is working

### Slow Writes

1. Increase `wal_buffers` in `compose.yml`
2. Verify `synchronous_commit = 'off'`
3. Check disk I/O performance
4. Increase connection pool size

### Disk Space Issues

1. Verify retention policy is active
2. Manually drop old chunks:
   ```sql
   SELECT drop_chunks('environment', INTERVAL '90 days');
   ```

## Migration from InfluxDB

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions and design rationale.

## License

MIT

## References

- [TimescaleDB Documentation](https://docs.timescale.com/)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
