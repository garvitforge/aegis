from aegis.grid import GridMap
from aegis.sensors import FourWayRangeSensor


def test_sensor_reveals_free_cells_and_first_obstacle() -> None:
    grid = GridMap(
        width=7,
        height=5,
        obstacles=frozenset({(4, 2), (2, 4)}),
    )

    observation = FourWayRangeSensor(max_range=5).sense(grid, (2, 2))

    assert (2, 2) in observation.free_cells
    assert (3, 2) in observation.free_cells
    assert (4, 2) in observation.obstacle_cells
    assert (5, 2) not in observation.free_cells


def test_sensor_respects_range() -> None:
    grid = GridMap(width=10, height=3)

    observation = FourWayRangeSensor(max_range=2).sense(grid, (1, 1))

    assert (3, 1) in observation.free_cells
    assert (4, 1) not in observation.free_cells
