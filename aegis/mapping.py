"""Partial-observability occupancy mapping for AEGIS."""

from dataclasses import dataclass

from .grid import Position


@dataclass
class OccupancyMap:
    """Map containing only what the robot has discovered."""

    width: int
    height: int
    known_free: set[Position]
    known_obstacles: set[Position]

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Map dimensions must be positive.")

        overlap = self.known_free & self.known_obstacles
        if overlap:
            raise ValueError(f"Cells cannot be both free and blocked: {overlap}")

        for position in self.known_free | self.known_obstacles:
            if not self.in_bounds(position):
                raise ValueError(f"Known cell {position} is outside the map.")

    def in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def is_known(self, position: Position) -> bool:
        return position in self.known_free or position in self.known_obstacles

    def update(
        self,
        free_cells: set[Position],
        obstacle_cells: set[Position],
    ) -> None:
        """Merge a new sensor observation into the map."""
        if free_cells & obstacle_cells:
            raise ValueError("A cell cannot be observed as both free and blocked.")

        self.known_free.update(free_cells)
        self.known_obstacles.update(obstacle_cells)
        self.known_free.difference_update(self.known_obstacles)
