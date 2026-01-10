import time
import logging
from typing import List, Dict, Any, Optional
from simulator import SensorDataPoint
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError

logger = logging.getLogger(__name__)


class InfluxService:
    def __init__(
        self,
        host: str,
        port: int,
        token: str,
        org: str,
        bucket: str,
    ):
        self.host = host
        self.port = port
        self.token = token
        self.org = org
        self.bucket = bucket
        self.url = f"http://{self.host}:{self.port}"
        self.client: Optional[InfluxDBClient] = None
        self.write_api = None
        self.query_api = None
        self._connect()

    def _connect(self):
        while True:
            try:
                self.client = InfluxDBClient(
                    url=self.url, token=self.token, org=self.org
                )
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                self.query_api = self.client.query_api()
                self.client.ping()
                logger.info("Connected to InfluxDB")
                break
            except Exception as e:
                logger.warning(f"Waiting for InfluxDB... {e}")
                time.sleep(5)

    def write(self, points: List[SensorDataPoint]) -> None:
        influx_points = []
        for point in points:
            p = Point(point["measurement"])
            for tag_key, tag_value in point.get("tags", {}).items():
                p = p.tag(tag_key, tag_value)
            for field_key, field_value in point.get("fields", {}).items():
                p = p.field(field_key, field_value)
            influx_points.append(p)

        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=influx_points)
        except InfluxDBError as e:
            logger.error(f"Error writing to InfluxDB: {e}")

    def query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a Flux query and return results as a list of dictionaries."""
        try:
            result = self.query_api.query(org=self.org, query=query)
            records = []
            for table in result:
                for record in table.records:
                    records.append(record.values)
            return records
        except Exception as e:
            logger.error(f"Error querying InfluxDB: {e}")
            return []
