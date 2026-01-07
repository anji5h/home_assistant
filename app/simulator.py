import random
from typing import List, TypedDict
from uuid import uuid4


class SensorTags(TypedDict):
    sensor_id: str
    location: str


class SensorFields(TypedDict):
    temperature: int
    humidity: int
    motion_detected: bool
    pressure: int
    uv_index: int

class SensorPoint(TypedDict):
    measurement: str
    tags: SensorTags
    fields: SensorFields


class SensorSimulator:
    def __init__(self, frequency: int = 100, batch_interval: int = 5) -> None:
        """
        :param frequency: The number of data points to generate every 'batch_interval' seconds.
        :param batch_interval: The interval (in seconds) at which to write the data.
        """
        self.frequency = frequency
        self.batch_interval = batch_interval
        self.locations: set = {
            "living_room",
            "kitchen",
            "bedroom",
            "bathroom",
            "garage",
            "balcony",
            "office",
        }

    def generate(self) -> List[SensorPoint]:
        """
        Generate data for the sensors and return a list of SensorPoint objects.
        The data for each 'batch_interval' will include 'frequency' number of data points.
        """
        sensor_data: List[SensorPoint] = []

        for _ in range(self.batch_interval):
            batch_data = []
            for _ in range(self.frequency):
                batch_data.append(
                    SensorPoint(
                        measurement="environment",
                        tags=SensorTags(
                            sensor_id=str(uuid4()),
                            location=random.choice(tuple(self.locations)),
                        ),
                        fields=SensorFields(
                            temperature=random.randint(-60, 60),
                            humidity=random.randint(20, 100),
                            motion_detected=bool(random.getrandbits(1)),
                            pressure=random.randint(900, 1050),
                            uv_index=random.randint(0, 11),
                        ),
                    ),
                )

            sensor_data.extend(batch_data)

        return sensor_data
