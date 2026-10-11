from dataclasses import replace

from aegis.benchmark import run_default_benchmark


def test_default_benchmark_is_reproducible() -> None:
    first = run_default_benchmark()
    second = run_default_benchmark()

    # Wall-clock planning latency is intentionally measured and therefore
    # varies between runs; compare the deterministic mission outputs only.
    assert [replace(result, average_planning_time_ms=0.0) for result in first] == [
        replace(result, average_planning_time_ms=0.0) for result in second
    ]
    assert all(result.coverage > 0.0 for result in first)
    assert all(result.replans > 0 for result in first)
    assert all(result.average_planning_time_ms >= 0.0 for result in first)
