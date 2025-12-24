from apscheduler.schedulers.background import BackgroundScheduler

def start_scheduler(simulator, influx):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=lambda: influx.write(simulator.generate()),
        trigger="interval",
        seconds=5,
        id="sensor_writer",
    )

    scheduler.add_job(
        func=lambda: influx.query(
            'SELECT MEAN("temperature") AS "avg_temp", '
            'MEAN("humidity") AS "avg_humidity" '
            'FROM "environment" '
            'WHERE time > now() - 1h '
            'GROUP BY "location"'
        ),
        trigger="interval",
        seconds=30,
        id="dashboard_refresh",
    )

    scheduler.start()