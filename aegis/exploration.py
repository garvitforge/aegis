"""Exploration utilities for partially known grid environments."""

from .grid import GridMap, Position


def frontier_cells(
    known_free: set[Position],
    known_obstacles: set[Position],
    width: int,
    height: int,
) -> set[Position]:
    """Find unexplored cells adjacent to known free space.

    A frontier is a cell that is inside the map, not known to be free or
    blocked, and directly adjacent to a known free cell.
    """
    frontiers: set[Position] = set()

    for x, y in known_free:
        for candidate in (
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ):
            cx, cy = candidate

            if not (0 <= cx < width and 0 <= cy < height):
                continue

            if candidate in known_free or candidate in known_obstacles:
                continue

            frontiers.add(candidate)

    return frontiers


def nearest_frontier(
    grid: GridMap,
    start: Position,
    frontiers: set[Position],
) -> Position | None:
    """Return the frontier with the shortest A* path from start."""
    if not frontiers:
        return None

    from .planning import astar

    candidates: list[tuple[int, Position]] = []

    for frontier in frontiers:
        try:
            path = astar(grid, start, frontier)
        except ValueError:
            continue

        candidates.append((len(path), frontier))

    if not candidates:
        return None

    return min(candidates, key=lambda item: (item[0], item[1]))[1]
