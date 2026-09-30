from aegis.exploration import frontier_cells, nearest_frontier
from aegis.grid import GridMap


def test_frontier_cells_are_unknown_neighbors_of_free_space() -> None:
    frontiers = frontier_cells(
        known_free={(1, 1)},
        known_obstacles={(0, 1)},
        width=3,
        height=3,
    )

    assert frontiers == {(1, 0), (1, 2), (2, 1)}


def test_nearest_frontier_chooses_shortest_reachable_frontier() -> None:
    grid = GridMap(5, 5, frozenset({(2, 1), (2, 2)}))

    result = nearest_frontier(
        grid,
        (0, 0),
        {(1, 0), (4, 4)},
    )

    assert result == (1, 0)


def test_no_frontier_returns_none() -> None:
    grid = GridMap(3, 3)
    assert nearest_frontier(grid, (1, 1), set()) is None
