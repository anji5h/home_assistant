import logging
from fastapi.concurrency import asynccontextmanager

from config import PostgresSettings
from postgres import PostgresService
from scheduler import start_scheduler
from simulator import SensorSimulator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """
    Application lifespan handler.
    All startup and shutdown logic lives here.
    """

    postgres: PostgresService = app.state.postgres
    simulator: SensorSimulator = app.state.simulator
    settings: PostgresSettings = app.state.settings
    workload = app.state.workload

    logger.info("Connecting to PostgreSQL...")
    await postgres.connect()

    logger.info("Starting background scheduler")
    scheduler = start_scheduler(simulator, postgres, settings, workload)

    try:
        yield
    finally:
        logger.info("Stopping background scheduler")
        if scheduler:
            scheduler.shutdown(wait=False)
        logger.info("Closing PostgreSQL connections")
        await postgres.close()
