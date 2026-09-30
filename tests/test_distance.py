import random

from aegis.autonomy import _shortest_known_path
from aegis.distance import bfs_tree, distance_map, path_from_tree
from aegis.generators import random_map
from aegis.mapping import OccupancyMap
from aegis.sensors import FourWayRangeSensor


def _partial_map(seed: int, steps: int = 12) -> tuple[OccupancyMap, tuple[int, int]]:
    """A partially explored map reached by a short random walk."""
    truth, start = random_map(12, 12, 0.2, seed)
    rng = random.Random(seed)
    sensor = FourWayRangeSensor(3)
    known = OccupancyMap(12, 12, set(), set())
    pos = start
    for _ in range(steps):
        obs = sensor.sense(truth, pos)
        known.update(set(obs.free_cells), set(obs.obstacle_cells))
        options = [n for n in ((pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)) if n in known.known_free]
        pos = options[int(rng.random() * len(options))]
    obs = sensor.sense(truth, pos)
    known.update(set(obs.free_cells), set(obs.obstacle_cells))
    return known, pos


def test_distance_map_matches_astar_path_lengths() -> None:
    for seed in range(25):
        known, pos = _partial_map(seed)
        distances = distance_map(known, pos)
        for cell in known.known_free:
            path = _shortest_known_path(known, pos, cell)
            if path is None:
                assert cell not in distances
            else:
                assert distances[cell] == len(path) - 1


def test_distance_map_is_empty_when_start_is_not_known_free() -> None:
    known = OccupancyMap(4, 4, {(1, 1)}, set())
    assert distance_map(known, (0, 0)) == {}
    assert bfs_tree(known, (0, 0)) == ({}, {})


def test_path_from_tree_is_contiguous_and_ends_at_goal() -> None:
    known, pos = _partial_map(3)
    distances, parent = bfs_tree(known, pos)
    goal = max(distances, key=lambda c: (distances[c], c))
    path = path_from_tree(parent, goal)
    assert path[0] == pos and path[-1] == goal
    assert len(path) - 1 == distances[goal]
    for a, b in zip(path, path[1:]):
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
    assert path_from_tree(parent, (99, 99)) is None
