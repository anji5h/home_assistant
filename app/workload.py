from config import WorkloadConfig, WorkloadProfile

WORKLOAD_PROFILES: dict[WorkloadProfile, WorkloadConfig] = {
    WorkloadProfile.LOW: WorkloadConfig(
        points_per_sec=250,
        num_writers=2,
        num_sensors=10000,
        min_pool_size=2,
        max_pool_size=5,
    ),
    WorkloadProfile.HIGH: WorkloadConfig(
        points_per_sec=750,
        num_writers=4,
        num_sensors=100000,
        min_pool_size=5,
        max_pool_size=15,
    ),
}
