import random
from datetime import datetime
from typing import Dict, List, Tuple, TypedDict

class SensorTags(TypedDict):
    sensor_id: str
    location: str

class SensorFields(TypedDict):
    temperature: float
    humidity: float
    motion_detected: bool

class SensorPoint(TypedDict):
    measurement: str
    tags: SensorTags
    fields: SensorFields

class SensorSimulator:
    def __init__(self, frequency: int = 60, batch_interval: int = 5) -> None:
        """
        :param frequency: The number of data points to generate every 'batch_interval' seconds.
        :param batch_interval: The interval (in seconds) at which to write the data.
        """
        self.frequency = frequency
        self.batch_interval = batch_interval
        self.sensors: Dict[str, str] = {
            "0": "living_room",
            "1": "kitchen",
            "2": "bedroom",
            "3": "bathroom",
            "4": "garage",
            "5": "balcony",
            "6": "office",
        }

        self.temp_ranges: Dict[str, Tuple[float, float]] = {
            "living_room": (18, 24),
            "kitchen": (20, 28),
            "bedroom": (16, 22),
            "bathroom": (18, 24),
            "garage": (12, 20),
            "balcony": (15, 25),
            "office": (18, 24),
        }

        self.humidity_ranges: Dict[str, Tuple[float, float]] = {
            "living_room": (40, 60),
            "kitchen": (45, 70),
            "bedroom": (35, 55),
            "bathroom": (50, 80),
            "garage": (30, 60),
            "balcony": (40, 65),
            "office": (40, 60),
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
                sensor_id = random.choice(list(self.sensors.keys()))
                location = self.sensors[sensor_id]
                temp_range = self.temp_ranges[location]
                humidity_range = self.humidity_ranges[location]

                batch_data.append(
                    SensorPoint(
                        measurement="environment",
                        tags=SensorTags(
                            sensor_id=f"sensor_{sensor_id}",
                            location=location,
                        ),
                        fields=SensorFields(
                            temperature=round(random.uniform(*temp_range), 2),
                            humidity=round(random.uniform(*humidity_range), 2),
                            motion_detected=bool(random.getrandbits(1)),
                        ),
                    )
                )

            sensor_data.extend(batch_data)

        return sensor_data
