from aegis.decision import frontier_candidates, frontier_candidates_reference
from aegis.distance import bfs_tree, distance_map, path_from_tree
from aegis.mapping import OccupancyMap


def test_bfs_distance_map_and_path_are_consistent() -> None:
    known = OccupancyMap(
        5,
        4,
        known_free={(x, y) for x in range(5) for y in range(4)} - {(2, 1)},
        known_obstacles={(2, 1)},
    )
    distances, parents = bfs_tree(known, (0, 0))
    goal = (4, 3)
    path = path_from_tree(parents, goal)

    assert distances[goal] == len(path) - 1
    assert path[0] == (0, 0)
    assert path[-1] == goal
    assert distance_map(known, (0, 0)) == distances
    assert path_from_tree(parents, (99, 99)) is None


def test_bfs_frontier_scoring_matches_reference_astar() -> None:
    known = OccupancyMap(
        6,
        5,
        known_free={(1, 1), (2, 1), (3, 1), (3, 2), (2, 2), (1, 2)},
        known_obstacles={(4, 2)},
    )
    assert frontier_candidates(known, (1, 1)) == frontier_candidates_reference(known, (1, 1))


def test_distance_map_is_empty_for_unknown_start() -> None:
    known = OccupancyMap(4, 4, {(1, 1)}, set())
    assert distance_map(known, (3, 3)) == {}
