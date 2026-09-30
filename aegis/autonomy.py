"""Closed-loop exploration controller for AEGIS."""

from dataclasses import dataclass

from .exploration import frontier_cells
from .grid import GridMap, Position
from .mapping import OccupancyMap
from .planning import astar
from .sensors import FourWayRangeSensor
from .state import RobotState


@dataclass
class ExplorationSimulator:
    """Simulate sensing and movement without exposing the hidden map to planning."""

    truth: GridMap
    robot: RobotState
    known: OccupancyMap
    sensor: FourWayRangeSensor

    def sense(self) -> None:
        observation = self.sensor.sense(self.truth, self.robot.position)
        self.known.update(
            set(observation.free_cells),
            set(observation.obstacle_cells),
        )

    def move_along(self, path: list[Position]) -> int:
        """Move through a known-safe path and return the number of steps."""
        if not path or path[0] != self.robot.position:
            raise ValueError("Path must start at the robot position.")

        for position in path[1:]:
            if position not in self.known.known_free:
                raise ValueError("Controller attempted to enter unknown space.")
            self.robot = self.robot.moved_to(position)

        return max(0, len(path) - 1)


def _shortest_known_path(
    known: OccupancyMap,
    start: Position,
    goal: Position,
) -> list[Position] | None:
    """A* over the discovered free space only."""
    if start not in known.known_free or goal not in known.known_free:
        return None

    unknown_cells = {
        (x, y)
        for x in range(known.width)
        for y in range(known.height)
        if (x, y) not in known.known_free
    }

    planning_grid = GridMap(
        width=known.width,
        height=known.height,
        obstacles=frozenset(unknown_cells | known.known_obstacles),
    )

    try:
        return astar(planning_grid, start, goal)
    except ValueError:
        return None


def _frontier_vantage(
    known: OccupancyMap,
    start: Position,
) -> tuple[Position, Position] | None:
    """Choose a frontier and a known-free cell from which to approach it."""
    frontiers = frontier_cells(
        known_free=known.known_free,
        known_obstacles=known.known_obstacles,
        width=known.width,
        height=known.height,
    )

    candidates: list[tuple[int, Position, Position]] = []

    for frontier in frontiers:
        x, y = frontier
        for vantage in (
            (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)
        ):
            if vantage not in known.known_free:
                continue

            path = _shortest_known_path(known, start, vantage)
            if path is not None:
                candidates.append((len(path), frontier, vantage))

    if not candidates:
        return None

    _, frontier, vantage = min(candidates, key=lambda item: (item[0], item[1]))
    return frontier, vantage


def explore(
    simulator: ExplorationSimulator,
    max_iterations: int = 100,
) -> int:
    """Run sense → plan → move → sense until exploration is exhausted."""
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive.")

    simulator.sense()
    iterations = 0

    while iterations < max_iterations:
        target = _frontier_vantage(simulator.known, simulator.robot.position)

        if target is None:
            break

        _, vantage = target
        path = _shortest_known_path(
            simulator.known,
            simulator.robot.position,
            vantage,
        )

        if path is None:
            break

        simulator.move_along(path)
        simulator.sense()
        iterations += 1

    return iterations
