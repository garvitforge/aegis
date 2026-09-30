"""Plain-text rendering of the robot's world (no dependencies)."""

from .grid import Position
from .mapping import OccupancyMap


def render_ascii(known: OccupancyMap, robot: Position, base: Position | None = None) -> str:
    """Draw the robot's current knowledge.

    ``#`` obstacle, ``.`` free, space = unknown, ``R`` robot, ``B`` base.
    """
    rows = []
    for y in range(known.height):
        row = []
        for x in range(known.width):
            cell = (x, y)
            if cell == robot:
                row.append("R")
            elif base is not None and cell == base:
                row.append("B")
            elif cell in known.known_obstacles:
                row.append("#")
            elif cell in known.known_free:
                row.append(".")
            else:
                row.append(" ")
        rows.append("".join(row))
    return "\n".join(rows)
