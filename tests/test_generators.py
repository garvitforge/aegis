import pytest

from aegis.generators import random_map, rooms_map
from aegis.trace import reachable_free_count


def _free_count(grid) -> int:
    return grid.width * grid.height - len(grid.obstacles)


def test_random_map_is_deterministic_per_seed() -> None:
    assert random_map(15, 15, 0.2, seed=4) == random_map(15, 15, 0.2, seed=4)
    assert random_map(15, 15, 0.2, seed=4) != random_map(15, 15, 0.2, seed=5)


def test_random_map_start_is_free_and_everything_is_reachable() -> None:
    for seed in range(20):
        grid, start = random_map(16, 16, 0.25, seed=seed)
        assert not grid.is_blocked(start)
        assert reachable_free_count(grid, start) == _free_count(grid)


def test_rooms_map_is_connected_and_has_walls() -> None:
    for seed in range(10):
        grid, start = rooms_map(20, 20, seed=seed)
        assert not grid.is_blocked(start)
        assert reachable_free_count(grid, start) == _free_count(grid)
        assert len(grid.obstacles) > 20


def test_generators_validate_arguments() -> None:
    with pytest.raises(ValueError):
        random_map(2, 2)
    with pytest.raises(ValueError):
        random_map(10, 10, obstacle_density=0.9)
    with pytest.raises(ValueError):
        random_map(10, 10, start=(50, 50))
    with pytest.raises(ValueError):
        rooms_map(5, 5)
