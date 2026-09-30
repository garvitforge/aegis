import pytest

from aegis.grid import GridMap
from aegis.planning import astar, manhattan


def test_manhattan_distance() -> None:
    assert manhattan((0, 0), (4, 3)) == 7


def test_astar_finds_shortest_open_grid_path() -> None:
    grid = GridMap(5, 5)
    path = astar(grid, (0, 0), (4, 4))

    assert path[0] == (0, 0)
    assert path[-1] == (4, 4)
    assert len(path) - 1 == 8


def test_astar_routes_around_obstacles() -> None:
    grid = GridMap(
        5,
        5,
        frozenset({(1, 0), (1, 1), (1, 2), (1, 3)}),
    )

    path = astar(grid, (0, 0), (2, 0))

    assert path[0] == (0, 0)
    assert path[-1] == (2, 0)
    assert all(not grid.is_blocked(position) for position in path)


def test_astar_rejects_blocked_start() -> None:
    grid = GridMap(3, 3, frozenset({(0, 0)}))

    with pytest.raises(ValueError):
        astar(grid, (0, 0), (2, 2))


def test_astar_reports_unreachable_goal() -> None:
    grid = GridMap(
        3,
        3,
        frozenset({(1, 0), (0, 1), (1, 1), (2, 1)}),
    )

    with pytest.raises(ValueError, match="No path exists"):
        astar(grid, (0, 0), (2, 2))
