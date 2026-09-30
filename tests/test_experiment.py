from aegis.experiment import (
    STRATEGIES,
    run_experiment,
    run_frontier_strategy,
    run_random_walk,
)
from aegis.generators import random_map


def test_experiment_is_reproducible() -> None:
    a = run_experiment(maps=3, size=12, seed=7)
    b = run_experiment(maps=3, size=12, seed=7)
    assert a == b


def test_frontier_strategies_fully_explore_small_maps() -> None:
    for seed in range(5):
        truth, start = random_map(12, 12, 0.2, seed)
        for name in ("nearest", "scored"):
            result = run_frontier_strategy(name, truth, start, 3, 600)
            assert result.completed
            assert result.final_coverage == 1.0
            assert result.moves == len(result.positions)


def test_coverage_never_decreases() -> None:
    truth, start = random_map(12, 12, 0.2, 1)
    for result in (
        run_frontier_strategy("scored", truth, start, 3, 600),
        run_random_walk(truth, start, 3, 300, seed=1),
    ):
        assert all(b >= a for a, b in zip(result.trace, result.trace[1:]))


def test_random_walk_is_deterministic_and_respects_budget() -> None:
    truth, start = random_map(12, 12, 0.2, 2)
    first = run_random_walk(truth, start, 3, 40, seed=9)
    second = run_random_walk(truth, start, 3, 40, seed=9)
    assert first == second
    assert first.moves <= 40


def test_frontier_strategies_beat_random_walk_on_average() -> None:
    report = run_experiment(maps=6, size=14, seed=3, max_moves=150)
    walk = report.summaries["random_walk"].mean_coverage_at[100]
    assert report.summaries["nearest"].mean_coverage_at[100] > walk
    assert report.summaries["scored"].mean_coverage_at[100] > walk
    assert set(report.summaries) == set(STRATEGIES)
