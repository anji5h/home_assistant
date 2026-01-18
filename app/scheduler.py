import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor

from config import PostgresSettings, WorkloadProfile
from postgres import PostgresService
from simulator import SensorSimulator
from workload import WORKLOAD_PROFILES

logger = logging.getLogger(__name__)


def start_scheduler(
    simulator: SensorSimulator,
    postgres: PostgresService,
    settings: PostgresSettings,
    workload_profile: WorkloadProfile,
) -> AsyncIOScheduler:
    """
    Starts background jobs for writing and querying PostgreSQL + TimescaleDB.
    
    Supports multiple concurrent writers based on workload profile:
    - LOW: 1 writer
    - HIGH: 4 writers
    
    Returns scheduler so lifespan can shut it down cleanly.
    """
    workload_config = WORKLOAD_PROFILES[workload_profile]
    num_writers = workload_config.num_writers

    scheduler = AsyncIOScheduler(
        executors={"default": AsyncIOExecutor()},
        job_defaults={
            "coalesce": True,
            "max_instances": num_writers,
            "misfire_grace_time": 5,
        },
    )

    def make_write_job(writer_id: int):
        """Factory function to create write job with proper closure."""
        async def write_job():
            """Write job for a single writer thread."""
            try:
                records = simulator.generate_batch()
                await postgres.write_batch(records, batch_size=1000)
                logger.debug(f"Writer {writer_id} wrote {len(records)} records")
            except Exception as e:
                logger.exception(f"Write job {writer_id} failed: {e}")
        return write_job

    # Create multiple writer jobs based on workload profile
    for writer_id in range(num_writers):
        scheduler.add_job(
            make_write_job(writer_id),
            trigger="interval",
            seconds=settings.write_interval,
            id=f"sensor_writer_{writer_id}",
            replace_existing=True,
        )

    async def read_job():
        """Read job for dashboard/analytics queries."""
        try:
            interval = '3 hour' if workload_profile == WorkloadProfile.HIGH else '1 hour'
            query = f"""
                SELECT
                    location,
                    AVG(temperature) as avg_temperature,
                    AVG(humidity) as avg_humidity,
                    AVG(pressure) as avg_pressure,
                    AVG(uv_index) as avg_uv_index
                FROM environment
                WHERE created_at > NOW() - INTERVAL '{interval}'
                GROUP BY location
                ORDER BY location;
                """
            await postgres.query(query)
            logger.debug(f"Read job executed successfully")
        except Exception as e:
            logger.exception("Read job failed: %s", e)

    scheduler.add_job(
        read_job,
        trigger="interval",
        seconds=settings.read_interval,
        id="dashboard_refresh",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started with {num_writers} writer(s) "
        f"({workload_profile} workload)"
    )

    return scheduler
