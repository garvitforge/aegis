from aegis.decision import (
    best_frontier,
    frontier_candidates,
    frontier_candidates_reference,
    nearest_frontier_candidate,
)
from aegis.generators import random_map
from aegis.mapping import OccupancyMap
from aegis.sensors import FourWayRangeSensor


def _states(seed: int):
    """Several partially explored states along one deterministic walk."""
    truth, start = random_map(14, 14, 0.2, seed)
    sensor = FourWayRangeSensor(3)
    known = OccupancyMap(14, 14, set(), set())
    pos = start
    for step in range(10):
        obs = sensor.sense(truth, pos)
        known.update(set(obs.free_cells), set(obs.obstacle_cells))
        yield OccupancyMap(14, 14, set(known.known_free), set(known.known_obstacles)), pos
        candidate = best_frontier(known, pos)
        if candidate is None:
            return
        pos = candidate.vantage


def test_fast_candidates_equal_reference_implementation() -> None:
    checked = 0
    for seed in range(20):
        for known, pos in _states(seed):
            assert frontier_candidates(known, pos) == frontier_candidates_reference(known, pos)
            checked += 1
    assert checked > 50


def test_no_candidates_when_start_unknown() -> None:
    known = OccupancyMap(5, 5, {(1, 1)}, set())
    assert frontier_candidates(known, (3, 3)) == []
    assert best_frontier(known, (3, 3)) is None
    assert nearest_frontier_candidate(known, (3, 3)) is None


def test_nearest_never_picks_a_farther_frontier_than_scored_has_available() -> None:
    for seed in range(10):
        for known, pos in _states(seed):
            nearest = nearest_frontier_candidate(known, pos)
            assert nearest is not None
            assert nearest.path_length == min(c.path_length for c in frontier_candidates(known, pos))
