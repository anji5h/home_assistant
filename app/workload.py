from config import WorkloadConfig, WorkloadProfile

WORKLOAD_PROFILES: dict[WorkloadProfile, WorkloadConfig] = {
    WorkloadProfile.LOW: WorkloadConfig(
        points_per_sec=25,
        num_writers=1,
        num_sensors=10000,
        min_pool_size=2,
        max_pool_size=5,
    ),
    WorkloadProfile.MEDIUM: WorkloadConfig(
        points_per_sec=100,
        num_writers=2,
        num_sensors=25000,
        min_pool_size=3,
        max_pool_size=8,
    ),
    WorkloadProfile.HIGH: WorkloadConfig(
        points_per_sec=750,
        num_writers=5,
        num_sensors=50000,
        min_pool_size=5,
        max_pool_size=15,
    ),
}
