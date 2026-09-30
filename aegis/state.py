"""Robot state primitives for AEGIS."""

from dataclasses import dataclass
from enum import Enum

from .grid import Position


class Heading(str, Enum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"


@dataclass(frozen=True)
class RobotState:
    """Minimal simulator state for a ground robot."""

    position: Position
    heading: Heading = Heading.NORTH
    battery: float = 100.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.battery <= 100.0:
            raise ValueError("Battery must be between 0 and 100.")

    def moved_to(self, position: Position, battery_cost: float = 0.1) -> "RobotState":
        """Return a new state after moving to a position."""
        if battery_cost < 0:
            raise ValueError("Battery cost cannot be negative.")

        return RobotState(
            position=position,
            heading=self.heading,
            battery=max(0.0, self.battery - battery_cost),
        )
