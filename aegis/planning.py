"""Path-planning algorithms for AEGIS."""

from heapq import heappop, heappush

from .grid import GridMap, Position


def manhattan(a: Position, b: Position) -> int:
    """Return the Manhattan distance between two grid positions."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid: GridMap, start: Position, goal: Position) -> list[Position]:
    """Find a shortest 4-connected path using A*.

    Returns a list including start and goal. Raises ValueError when the
    endpoints are invalid or no path exists.
    """
    if not grid.in_bounds(start) or not grid.in_bounds(goal):
        raise ValueError("Start and goal must be inside the grid.")

    if grid.is_blocked(start) or grid.is_blocked(goal):
        raise ValueError("Start and goal cannot be obstacles.")

    frontier: list[tuple[int, int, Position]] = []
    heappush(frontier, (manhattan(start, goal), 0, start))

    came_from: dict[Position, Position | None] = {start: None}
    cost_so_far: dict[Position, int] = {start: 0}
    sequence = 0

    while frontier:
        _, _, current = heappop(frontier)

        if current == goal:
            break

        for neighbor in grid.neighbors(current):
            new_cost = cost_so_far[current] + 1

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + manhattan(neighbor, goal)
                sequence += 1
                heappush(frontier, (priority, sequence, neighbor))
                came_from[neighbor] = current

    if goal not in came_from:
        raise ValueError("No path exists between start and goal.")

    path: list[Position] = []
    current: Position | None = goal

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path
