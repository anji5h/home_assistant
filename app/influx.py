import time
from influxdb import InfluxDBClient

class InfluxService:
    def __init__(self, host="influxdb", port=8086, db_name="home_assistant"):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = None
        self._connect()

    def _connect(self):
        while True:
            try:
                self.client = InfluxDBClient(
                    host=self.host,
                    port=self.port
                )
                self.client.create_database(self.db_name)
                self.client.switch_database(self.db_name)
                print("Connected to InfluxDB")
                break
            except Exception as e:
                print("Waiting for InfluxDB...", e)
                time.sleep(5)

    def write(self, points):
        self.client.write_points(points)

    def query(self, query: str):
        result = self.client.query(query)
        return list(result.get_points())