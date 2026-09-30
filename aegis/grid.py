"""Grid-world representation used by the AEGIS simulator."""

from dataclasses import dataclass
from typing import Iterable


Position = tuple[int, int]


@dataclass(frozen=True)
class GridMap:
    """A rectangular grid where True cells are obstacles."""

    width: int
    height: int
    obstacles: frozenset[Position] = frozenset()

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Grid dimensions must be positive.")

        for x, y in self.obstacles:
            if not self.in_bounds((x, y)):
                raise ValueError(f"Obstacle {(x, y)} is outside the grid.")

    def in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, position: Position) -> bool:
        return position in self.obstacles

    def neighbors(self, position: Position) -> Iterable[Position]:
        x, y = position

        candidates = (
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        )

        for candidate in candidates:
            if self.in_bounds(candidate) and not self.is_blocked(candidate):
                yield candidate
