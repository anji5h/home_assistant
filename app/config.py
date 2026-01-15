from enum import Enum
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Tuple


class WorkloadProfile(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PostgresSettings(BaseSettings):
    """PostgreSQL + TimescaleDB connection settings."""
    postgres_host: str = Field(default="postgres", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_database: str = Field(default="home_assistant", env="POSTGRES_DATABASE")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    
    workload: WorkloadProfile = Field(
        default=WorkloadProfile.LOW, env="WORKLOAD"
    )
    write_interval: int = Field(default=10, env="WRITE_INTERVAL")
    read_interval: int = Field(default=20, env="READ_INTERVAL")

    class Config:
        env_file = ".env"
        case_sensitive = False


class WorkloadConfig:
    """Workload profile configuration."""
    def __init__(
        self,
        points_per_sec: int,
        num_writers: int,
        num_sensors: int,
        min_pool_size: int,
        max_pool_size: int,
    ):
        self.points_per_sec = points_per_sec
        self.num_writers = num_writers
        self.num_sensors = num_sensors
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size