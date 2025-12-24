import random
from datetime import datetime
from typing import Dict, List, Tuple, TypedDict

class SensorTags(TypedDict):
    sensor_id: str
    location: str
    timestamp: str

class SensorFields(TypedDict):
    temperature: float
    humidity: float
    motion_detected: bool

class SensorPoint(TypedDict):
    measurement: str
    tags: SensorTags
    fields: SensorFields

class SensorSimulator:
    def __init__(self) -> None:
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
        sensor_data: List[SensorPoint] = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for _ in range(20):
            sensor_id = random.choice(list(self.sensors.keys()))
            location = self.sensors[sensor_id]
            temp_range = self.temp_ranges[location]
            humidity_range = self.humidity_ranges[location]

            sensor_data.append(
                SensorPoint(
                    measurement="environment",
                    tags=SensorTags(
                        sensor_id=f"sensor_{sensor_id}",
                        location=location,
                        timestamp=current_time,
                    ),
                    fields=SensorFields(
                        temperature=round(random.uniform(*temp_range), 2),
                        humidity=round(random.uniform(*humidity_range), 2),
                        motion_detected=bool(random.getrandbits(1)),
                    ),
                )
            )

        return sensor_data
