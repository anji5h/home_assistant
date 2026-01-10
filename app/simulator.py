import random
from typing import List, TypedDict
from uuid import uuid4


class SensorTags(TypedDict):
    sensor_id: str
    location: str


class SensorFields(TypedDict):
    temperature: float
    humidity: int
    motion_detected: bool
    pressure: int
    uv_index: int


class SensorDataPoint(TypedDict):
    measurement: str
    tags: SensorTags
    fields: SensorFields


class SensorSimulator:
    def __init__(
        self, points_per_batch: int = 100, batch_interval_seconds: int = 5
    ) -> None:
        """
        Initialize the sensor data simulator.

        :param points_per_batch: Number of individual sensor readings to generate in each batch.
        This controls how many data points are produced every batch_interval_seconds.

        :param batch_interval_seconds: 
        Time interval (in seconds) at which a full batch of data is emitted.
        """
        self.points_per_batch = points_per_batch
        self.batch_interval_seconds = batch_interval_seconds
        self.room_locations = {
            "living_room",
            "kitchen",
            "bedroom",
            "bathroom",
            "garage",
            "balcony",
            "office",
        }

    def generate_batch(self) -> List[SensorDataPoint]:
        """
        Generate a batch of simulated sensor data points.

        One batch represents the data collected over `batch_interval_seconds`,
        containing `points_per_batch` individual readings (e.g., one per sensor or per event).

        Returns:
            A list of SensorDataPoint objects ready for writing to InfluxDB.
        """
        batch_data: List[SensorDataPoint] = []

        for _ in range(self.batch_interval_seconds):
            second_readings: List[SensorDataPoint] = []

            for _ in range(self.points_per_batch // self.batch_interval_seconds + 1):
                if (
                    len(second_readings) * self.batch_interval_seconds
                    >= self.points_per_batch
                ):
                    break

                sensor_reading = SensorDataPoint(
                    measurement="environment",
                    tags=SensorTags(
                        sensor_id=str(uuid4()),
                        location=random.choice(tuple(self.room_locations)),
                    ),
                    fields=SensorFields(
                        temperature=round(random.uniform(-60, 60), 2),
                        humidity=random.randint(20, 100),
                        motion_detected=bool(random.getrandbits(1)),
                        pressure=random.randint(900, 1050),
                        uv_index=random.randint(0, 11),
                    ),
                )
                second_readings.append(sensor_reading)

            batch_data.extend(second_readings)

        if len(batch_data) > self.points_per_batch:
            batch_data = batch_data[: self.points_per_batch]

        return batch_data
