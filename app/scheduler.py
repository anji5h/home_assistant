from apscheduler.schedulers.background import BackgroundScheduler

def start_scheduler(simulator, influx, config):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=lambda: influx.write(simulator.generate()),
        trigger="interval",
        seconds=int(config.get("INFLUX_WRITE_INTERVAL", 5)),
        id="sensor_writer",
    )

    scheduler.add_job(
        func=lambda: influx.query(
            f'''
            from(bucket: "{influx.bucket}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "environment")
            |> filter(fn: (r) => r["_field"] == "temperature" or r["_field"] == "humidity")
            |> group(columns: ["location", "_field"])
            |> mean()
            |> pivot(rowKey: ["location"], columnKey: ["_field"], valueColumn: "_value")
            |> map(fn: (r) => ({{
                location: r.location,
                avg_temp: r.temperature,
                avg_humidity: r.humidity
            }}))
            '''
        ),
        trigger="interval",
        seconds=int(config.get("INFLUX_READ_INTERVAL", 30)),
        id="dashboard_refresh",
    )

    scheduler.start()