"""Seeded map generators so experiments are reproducible.

Every generator returns ``(GridMap, start)``. All free cells are guaranteed to
be reachable from ``start``: any free cell that would be cut off is filled in.
"""

import random
from collections import deque

from .grid import GridMap, Position


def _reachable(width: int, height: int, obstacles: set[Position], start: Position) -> set[Position]:
    seen = {start}
    queue: deque[Position] = deque([start])
    while queue:
        x, y = queue.popleft()
        for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if nb in seen or nb in obstacles:
                continue
            if 0 <= nb[0] < width and 0 <= nb[1] < height:
                seen.add(nb)
                queue.append(nb)
    return seen


def _seal_unreachable(width: int, height: int, obstacles: set[Position], start: Position) -> GridMap:
    reachable = _reachable(width, height, obstacles, start)
    sealed = set(obstacles)
    for x in range(width):
        for y in range(height):
            if (x, y) not in reachable:
                sealed.add((x, y))
    return GridMap(width, height, frozenset(sealed))


def random_map(
    width: int,
    height: int,
    obstacle_density: float = 0.2,
    seed: int = 0,
    start: Position = (1, 1),
    min_free_fraction: float = 0.5,
) -> tuple[GridMap, Position]:
    """Scatter obstacles at random, keeping only the region reachable from start."""
    if width < 3 or height < 3:
        raise ValueError("Map must be at least 3x3.")
    if not 0.0 <= obstacle_density < 0.6:
        raise ValueError("obstacle_density must be in [0.0, 0.6).")
    if not (0 <= start[0] < width and 0 <= start[1] < height):
        raise ValueError("start must be inside the map.")

    rng = random.Random(seed)
    target = min_free_fraction * width * height

    best: GridMap | None = None
    for _ in range(200):
        obstacles = {
            (x, y)
            for x in range(width)
            for y in range(height)
            if (x, y) != start and rng.random() < obstacle_density
        }
        grid = _seal_unreachable(width, height, obstacles, start)
        free = width * height - len(grid.obstacles)
        if best is None or free > width * height - len(best.obstacles):
            best = grid
        if free >= target:
            return grid, start

    assert best is not None
    return best, start


def rooms_map(
    width: int,
    height: int,
    room_size: int = 6,
    seed: int = 0,
    start: Position = (1, 1),
) -> tuple[GridMap, Position]:
    """A building-like map: rectangular rooms joined by single-cell doors."""
    if width < 7 or height < 7:
        raise ValueError("Map must be at least 7x7 for rooms.")
    if room_size < 3:
        raise ValueError("room_size must be at least 3.")
    if not (0 <= start[0] < width and 0 <= start[1] < height):
        raise ValueError("start must be inside the map.")

    rng = random.Random(seed)
    pitch = room_size + 1
    wall_xs = list(range(pitch, width - 1, pitch))
    wall_ys = list(range(pitch, height - 1, pitch))
    obstacles: set[Position] = set()

    for wx in wall_xs:
        for y in range(height):
            obstacles.add((wx, y))
    for wy in wall_ys:
        for x in range(width):
            obstacles.add((x, wy))

    # One door per wall segment (between two wall crossings or the map edge).
    y_bounds = [-1] + wall_ys + [height]
    for wx in wall_xs:
        for lo, hi in zip(y_bounds, y_bounds[1:]):
            cells = list(range(lo + 1, hi))
            if cells:
                obstacles.discard((wx, cells[int(rng.random() * len(cells))]))
    x_bounds = [-1] + wall_xs + [width]
    for wy in wall_ys:
        for lo, hi in zip(x_bounds, x_bounds[1:]):
            cells = list(range(lo + 1, hi))
            if cells:
                obstacles.discard((cells[int(rng.random() * len(cells))], wy))

    obstacles.discard(start)
    return _seal_unreachable(width, height, obstacles, start), start


GENERATORS = {"random": random_map, "rooms": rooms_map}
