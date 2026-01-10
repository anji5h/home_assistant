import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from influx import InfluxService
from simulator import SensorSimulator
from scheduler import start_scheduler

# Load environment variables from .env file
load_dotenv()

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="Home Assistant", description="Smart Home Sensor Simulator", version="1.0.0"
)

influx = InfluxService(
    host=os.getenv("INFLUXDB_HOST", "influxdb"),
    port=int(os.getenv("INFLUXDB_PORT", "8086")),
    token=os.getenv("INFLUXDB_TOKEN", ""),
    org=os.getenv("INFLUXDB_ORG", "ut"),
    bucket=os.getenv("INFLUXDB_BUCKET", "home_assistant"),
)
simulator = SensorSimulator(
    points_per_batch=int(os.getenv("SIMULATOR_POINTS_PER_BATCH", "100")),
    batch_interval_seconds=int(os.getenv("SIMULATOR_BATCH_INTERVAL_SECONDS", "5")),
)


@app.on_event("startup")
def startup():
    start_scheduler(simulator, influx, os.environ)


@app.get("/health")
def health():
    return {"status": "running"}


@app.get("/locations")
def locations():
    return list(simulator.room_locations)


@app.get("/temperature/average")
def average_temperature(location: str | None = None, hours: int = 1):
    location_filter = (
        f'|> filter(fn: (r) => r["location"] == "{location}")' if location else ""
    )
    query = f"""
        from(bucket: "{influx.bucket}")
        |> range(start: -{hours}h)
        |> filter(fn: (r) => r["_measurement"] == "environment")
        |> filter(fn: (r) => r["_field"] == "temperature")
        {location_filter}
        |> mean()
    """
    return influx.query(query)


@app.get("/latest")
def latest_readings(limit: int = 20):
    query = f"""
        from(bucket: "{influx.bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == "environment")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: {limit})
    """
    return influx.query(query)
