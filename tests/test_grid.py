from aegis.grid import GridMap


def test_neighbors_stay_in_bounds_and_avoid_obstacles() -> None:
    grid = GridMap(3, 3, frozenset({(1, 0)}))

    assert set(grid.neighbors((0, 0))) == {(0, 1)}


def test_obstacle_outside_grid_is_rejected() -> None:
    try:
        GridMap(3, 3, frozenset({(3, 1)}))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
