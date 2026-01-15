import logging
from fastapi import FastAPI
from lifespan import lifespan
from workload import WORKLOAD_PROFILES
from config import PostgresSettings
from postgres import PostgresService
from simulator import SensorSimulator

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

settings = PostgresSettings()
workload = WORKLOAD_PROFILES[settings.workload]

app = FastAPI(
    title="Home Assistant",
    description="Smart Home Sensor Simulator with PostgreSQL + TimescaleDB",
    version="2.0.0",
    lifespan=lifespan,
)

postgres = PostgresService(
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_database,
    user=settings.postgres_user,
    password=settings.postgres_password,
    min_pool_size=workload.min_pool_size,
    max_pool_size=workload.max_pool_size,
)

simulator = SensorSimulator(
    points_per_sec=workload.points_per_sec,
    num_sensors=workload.num_sensors,
)

app.state.postgres = postgres
app.state.simulator = simulator
app.state.settings = settings
app.state.workload = settings.workload


@app.get("/health")
def health():
    return {
        "status": "running",
        "workload": settings.workload.value,
        "points_per_sec": workload.points_per_sec,
        "num_writers": workload.num_writers,
        "num_sensors": workload.num_sensors,
    }
