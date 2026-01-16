from config import WorkloadConfig, WorkloadProfile

WORKLOAD_PROFILES: dict[WorkloadProfile, WorkloadConfig] = {
    WorkloadProfile.LOW: WorkloadConfig(
        points_per_sec=100,
        num_writers=1,
        num_sensors=10000,
        min_pool_size=2,
        max_pool_size=5,
    ),
    WorkloadProfile.HIGH: WorkloadConfig(
        points_per_sec=1000,
        num_writers=3,
        num_sensors=100000,
        min_pool_size=5,
        max_pool_size=15,
    ),
}
