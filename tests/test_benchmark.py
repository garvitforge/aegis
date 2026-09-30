from aegis.benchmark import run_default_benchmark


def test_default_benchmark_is_reproducible() -> None:
    first = run_default_benchmark()
    second = run_default_benchmark()
    assert first == second
    assert all(result.coverage > 0.0 for result in first)
    assert all(result.replans > 0 for result in first)
