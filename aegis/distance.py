"""Breadth-first distance maps over discovered free space."""

from collections import deque

from .grid import Position
from .mapping import OccupancyMap


def bfs_tree(
    known: OccupancyMap, start: Position
) -> tuple[dict[Position, int], dict[Position, Position | None]]:
    """Return shortest distances and parents for reachable known-free cells."""
    if start not in known.known_free:
        return {}, {}
    distance: dict[Position, int] = {start: 0}
    parent: dict[Position, Position | None] = {start: None}
    queue: deque[Position] = deque([start])
    while queue:
        x, y = queue.popleft()
        current = (x, y)
        for neighbor in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if neighbor in distance or neighbor not in known.known_free:
                continue
            distance[neighbor] = distance[current] + 1
            parent[neighbor] = current
            queue.append(neighbor)
    return distance, parent


def distance_map(known: OccupancyMap, start: Position) -> dict[Position, int]:
    """Shortest move count from start to every reachable known-free cell."""
    return bfs_tree(known, start)[0]


def path_from_tree(
    parent: dict[Position, Position | None], goal: Position
) -> list[Position] | None:
    """Rebuild the start-to-goal path from a BFS parent map."""
    if goal not in parent:
        return None
    path: list[Position] = []
    current: Position | None = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path
