"""
PostgreSQL + TimescaleDB service for sensor data ingestion.

This module provides a production-quality PostgreSQL service optimized for:
- High-throughput time-series data ingestion
- Batched inserts for efficiency
- Connection pooling for concurrent writers
- Stable memory usage (avoids InfluxDB-style unbounded growth)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import asyncpg
from asyncpg.pool import Pool

logger = logging.getLogger(__name__)


class PostgresService:
    """
    PostgreSQL service with TimescaleDB for time-series sensor data.
    
    Uses asyncpg for async/await support and connection pooling.
    Implements batched inserts for optimal write performance.
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        min_pool_size: int = 2,
        max_pool_size: int = 10,
    ):
        """
        Initialize PostgreSQL service with connection pool.
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Database user
            password: Database password
            min_pool_size: Minimum pool size (for LOW workload)
            max_pool_size: Maximum pool size (for HIGH workload with concurrent writers)
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.pool: Optional[Pool] = None

    async def connect(self) -> None:
        """Establish connection pool to PostgreSQL."""
        while True:
            try:
                self.pool = await asyncpg.create_pool(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    min_size=self.min_pool_size,
                    max_size=self.max_pool_size,
                    command_timeout=60,
                    server_settings={
                        'application_name': 'home_assistant_ingestion',
                    }
                )
                # Test connection
                async with self.pool.acquire() as conn:
                    await conn.execute('SELECT 1')
                    # Verify TimescaleDB extension
                    result = await conn.fetchval(
                        "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'timescaledb')"
                    )
                    if not result:
                        raise RuntimeError("TimescaleDB extension not enabled")
                logger.info(
                    f"Connected to PostgreSQL at {self.host}:{self.port}/{self.database}"
                )
                break
            except Exception as e:
                logger.warning(f"Waiting for PostgreSQL... {e}")
                await asyncio.sleep(5)

    async def close(self) -> None:
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")

    async def write_batch(
        self, 
        records: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> None:
        """
        Write a batch of sensor records using efficient bulk insert.
        
        Uses COPY or prepared INSERT statements for optimal performance.
        Batches are split into smaller chunks to avoid memory issues.
        
        Args:
            records: List of sensor records with keys:
                - created_at: datetime or timestamp
                - sensor_id: int
                - location: str
                - temperature: float
                - humidity: int
                - pressure: int
                - uv_index: int
            batch_size: Number of records per batch (default 1000)
        """
        if not self.pool:
            raise RuntimeError("PostgreSQL connection pool not initialized")

        if not records:
            return

        # Split into batches to avoid memory issues
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            try:
                async with self.pool.acquire() as conn:
                    # Use COPY for maximum performance (fastest bulk insert)
                    # This is more efficient than individual INSERTs
                    await conn.copy_records_to_table(
                        'environment',
                        records=[
                            (
                                r['created_at'],
                                r['sensor_id'],
                                r['location'],
                                r['temperature'],
                                r['humidity'],
                                r['pressure'],
                                r['uv_index']
                            )
                            for r in batch
                        ],
                        columns=[
                            'created_at',
                            'sensor_id',
                            'location',
                            'temperature',
                            'humidity',
                            'pressure',
                            'uv_index'
                        ]
                    )
            except Exception as e:
                logger.error(f"Error writing batch to PostgreSQL: {e}")
                # Optionally retry or handle error
                raise

    async def query(
        self, 
        query: str, 
        *args
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dictionaries.
        
        Args:
            query: SQL query string
            *args: Query parameters
        
        Returns:
            List of dictionaries representing query results
        """
        if not self.pool:
            raise RuntimeError("PostgreSQL connection pool not initialized")

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error querying PostgreSQL: {e}")
            return []

    async def get_stats(self) -> Dict[str, Any]:
        """Get current database statistics."""
        result = await self.query("SELECT * FROM get_environment_stats()")
        if result:
            return result[0]
        return {}
