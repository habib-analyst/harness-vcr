"""Paired-bootstrap statistics over tasks.

All four pairings are evaluated on the SAME task list, so every
contrast below is paired at the task level: resampling resamples task
indices and recomputes every cell from the same resample. CIs are
percentile 95% intervals. The bootstrap RNG is seeded, so reruns
reproduce the digest exactly.
"""
import random


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def paired_bootstrap(per_task, fn, reps=2000, seed=12345):
    """per_task: list of per-task records; fn: record-list -> float.

    Returns (point_estimate, (lo, hi)).
    """
    n = len(per_task)
    rng = random.Random(seed)
    point = fn(per_task)
    boots = []
    for _ in range(reps):
        sample = [per_task[rng.randrange(n)] for _ in range(n)]
        boots.append(fn(sample))
    boots.sort()
    lo = boots[int(0.025 * reps)]
    hi = boots[int(0.975 * reps) - 1]
    return point, (lo, hi)
