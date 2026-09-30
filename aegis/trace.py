"""Rebuild what the robot knew after every move, from a list of positions.

The simulation is deterministic, so the sequence of positions a mission visited
is enough to reconstruct the occupancy map at every step. This is used for
coverage curves and for animated replays.
"""

from collections.abc import Iterator

from .grid import GridMap, Position
from .mapping import OccupancyMap
from .sensors import FourWayRangeSensor


def reachable_free_count(truth: GridMap, start: Position) -> int:
    """Number of free cells connected to start (the most a robot could ever see)."""
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if nb not in seen and truth.in_bounds(nb) and not truth.is_blocked(nb):
                seen.add(nb)
                stack.append(nb)
    return len(seen)


def replay_states(
    truth: GridMap,
    start: Position,
    positions: list[Position],
    sensor_range: int,
) -> Iterator[tuple[Position, OccupancyMap]]:
    """Yield (robot position, known map) after the first scan and after each move.

    The yielded map is a snapshot; it is safe to keep.
    """
    sensor = FourWayRangeSensor(sensor_range)
    known = OccupancyMap(truth.width, truth.height, set(), set())

    def scan(pos: Position) -> None:
        obs = sensor.sense(truth, pos)
        known.update(set(obs.free_cells), set(obs.obstacle_cells))

    scan(start)
    yield start, OccupancyMap(truth.width, truth.height, set(known.known_free), set(known.known_obstacles))
    for pos in positions:
        scan(pos)
        yield pos, OccupancyMap(truth.width, truth.height, set(known.known_free), set(known.known_obstacles))


def coverage_trace(
    truth: GridMap,
    start: Position,
    positions: list[Position],
    sensor_range: int,
) -> list[float]:
    """Fraction of reachable free cells discovered, after the first scan and each move."""
    total = reachable_free_count(truth, start)
    return [len(known.known_free) / total for _, known in replay_states(truth, start, positions, sensor_range)]
