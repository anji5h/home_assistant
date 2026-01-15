import random
from typing import List, Dict, Any
from datetime import datetime, timezone


class SensorSimulator:
    """
    Sensor data simulator for PostgreSQL + TimescaleDB.

    Generates sensor data with bounded integer sensor_id (replaces UUID)
    for efficient storage and indexing.
    """

    def __init__(self, points_per_sec: int, num_sensors: int) -> None:
        """
        Initialize the sensor data simulator.

        Args:
            points_per_sec (int): Number of data points to generate per second.
            num_sensors (int): Total number of unique sensors (bounded integer range).
        """
        self.points_per_sec = points_per_sec
        self.num_sensors = num_sensors
        self.sensor_locations = (
            "living_room",
            "kitchen",
            "bedroom",
            "bathroom",
            "garage",
            "garden",
            "basement",
            "attic",
        )

    def generate_batch(self) -> List[Dict[str, Any]]:
        """
        Generate a batch of simulated sensor data points.

        Returns:
            List of dictionaries with sensor data ready for PostgreSQL insertion.
        """
        records = []
        now = datetime.now(timezone.utc)

        for _ in range(self.points_per_sec):
            sensor_id = random.randint(0, self.num_sensors - 1)
            location = random.choice(self.sensor_locations)

            record = {
                "created_at": now,
                "sensor_id": sensor_id,
                "location": location,
                "temperature": round(random.uniform(-60, 60), 2),
                "humidity": random.randint(20, 100),
                "pressure": random.randint(900, 1050),
                "uv_index": random.randint(0, 11),
            }
            records.append(record)

        return records
