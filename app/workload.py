from config import WorkloadConfig, WorkloadProfile

WORKLOAD_PROFILES: dict[WorkloadProfile, WorkloadConfig] = {
    WorkloadProfile.LOW: WorkloadConfig(
        points_per_sec=25,
        num_writers=1,
        num_sensors=10000,
        min_pool_size=2,
        max_pool_size=5,
    ),
    WorkloadProfile.HIGH: WorkloadConfig(
        points_per_sec=500,
        num_writers=4,
        num_sensors=50000,
        min_pool_size=5,
        max_pool_size=15,
    ),
}
