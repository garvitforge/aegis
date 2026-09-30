"""Deterministic simulated range sensor for AEGIS."""

from dataclasses import dataclass

from .grid import GridMap, Position


@dataclass(frozen=True)
class SensorObservation:
    """Cells revealed by one sensor scan."""

    free_cells: frozenset[Position]
    obstacle_cells: frozenset[Position]


class FourWayRangeSensor:
    """Idealized four-direction sensor with a configurable range.

    The sensor is intentionally simple and deterministic. It reveals cells
    along the four cardinal rays and stops a ray at the first obstacle.
    """

    _DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def __init__(self, max_range: int = 3) -> None:
        if max_range <= 0:
            raise ValueError("Sensor range must be positive.")
        self.max_range = max_range

    def sense(self, grid: GridMap, position: Position) -> SensorObservation:
        if not grid.in_bounds(position):
            raise ValueError("Sensor position is outside the grid.")
        if grid.is_blocked(position):
            raise ValueError("Sensor cannot be placed on an obstacle.")

        free = {position}
        obstacles: set[Position] = set()

        for dx, dy in self._DIRECTIONS:
            for distance in range(1, self.max_range + 1):
                cell = (
                    position[0] + dx * distance,
                    position[1] + dy * distance,
                )

                if not grid.in_bounds(cell):
                    break

                if grid.is_blocked(cell):
                    obstacles.add(cell)
                    break

                free.add(cell)

        return SensorObservation(
            free_cells=frozenset(free),
            obstacle_cells=frozenset(obstacles),
        )
