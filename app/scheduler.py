from influx import InfluxService
from simulator import SensorSimulator
from apscheduler.schedulers.background import BackgroundScheduler


def start_scheduler(simulator: SensorSimulator, influx: InfluxService, config: dict):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=lambda: influx.write(simulator.generate_batch()),
        trigger="interval",
        seconds=int(config.get("INFLUX_WRITE_INTERVAL", 5)),
        id="sensor_writer",
    )

    scheduler.add_job(
        func=lambda: influx.query(
            f"""
            from(bucket: "{influx.bucket}")
            |> range(start: -10m)
            |> filter(fn: (r) => r["_measurement"] == "environment")
            |> filter(fn: (r) =>
                r["_field"] == "temperature" or
                r["_field"] == "humidity" or
                r["_field"] == "pressure" or
                r["_field"] == "uv_index"
            )
            |> group(columns: ["location", "_field"])
            |> mean()
            |> pivot(
                rowKey: ["location"],
                columnKey: ["_field"],
                valueColumn: "_value"
            )"""
        ),
        trigger="interval",
        seconds=int(config.get("INFLUX_READ_INTERVAL", 30)),
        id="dashboard_refresh",
    )

    scheduler.start()
