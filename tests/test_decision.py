from aegis.decision import best_frontier, frontier_candidates
from aegis.mapping import OccupancyMap


def test_frontier_candidates_are_reachable_and_scored() -> None:
    known = OccupancyMap(
        6,
        5,
        known_free={(1, 1), (2, 1), (3, 1), (3, 2)},
        known_obstacles={(2, 2)},
    )

    candidates = frontier_candidates(known, (1, 1))

    assert candidates
    assert all(c.path_length >= 0 for c in candidates)
    assert all(c.information_gain >= 0 for c in candidates)
    assert candidates == sorted(
        candidates, key=lambda c: (-c.score, c.path_length, c.frontier, c.vantage)
    )


def test_best_frontier_is_deterministic() -> None:
    known = OccupancyMap(5, 5, {(1, 1), (2, 1), (3, 1)}, set())
    first = best_frontier(known, (1, 1))
    second = best_frontier(known, (1, 1))
    assert first == second
