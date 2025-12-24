from fastapi import FastAPI
from influx import InfluxService
from simulator import SensorSimulator
from scheduler import start_scheduler

app = FastAPI(
    title="Home Assistant",
    description="Smart Home Sensor Simulator",
    version="1.0.0"
)

influx = InfluxService()
simulator = SensorSimulator()

@app.on_event("startup")
def startup():
    start_scheduler(simulator, influx)

@app.get("/health")
def health():
    return {"status": "running"}

@app.get("/locations")
def locations():
    return list(simulator.sensors.values())

@app.get("/temperature/average")
def average_temperature(location: str | None = None, hours: int = 1):
    where = f"AND location='{location}'" if location else ""
    query = f"""
        SELECT MEAN("temperature")
        FROM "environment"
        WHERE time > now() - {hours}h {where}
    """
    return influx.query(query)

@app.get("/latest")
def latest_readings(limit: int = 20):
    query = f"""
        SELECT *
        FROM "environment"
        ORDER BY time DESC
        LIMIT {limit}
    """
    return influx.query(query)
