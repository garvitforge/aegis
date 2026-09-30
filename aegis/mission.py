"""Mission-level autonomy and telemetry for AEGIS."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from .autonomy import _shortest_known_path
from .decision import FrontierCandidate, best_frontier
from .mapping import OccupancyMap
from .metrics import MissionMetrics
from .sensors import FourWayRangeSensor
from .state import RobotState
from .grid import GridMap


@dataclass
class Mission:
    truth: GridMap
    robot: RobotState
    known: OccupancyMap
    sensor: FourWayRangeSensor
    metrics: MissionMetrics
    battery_reserve: float = 20.0
    base_position: tuple[int, int] | None = None
    # Strategy used to pick the next frontier. Swappable so strategies can be benchmarked.
    frontier_selector: Callable[
        [OccupancyMap, tuple[int, int]], FrontierCandidate | None
    ] = best_frontier

    def sense(self) -> None:
        before = len(self.known.known_free) + len(self.known.known_obstacles)
        observation = self.sensor.sense(self.truth, self.robot.position)
        self.known.update(set(observation.free_cells), set(observation.obstacle_cells))
        after = len(self.known.known_free) + len(self.known.known_obstacles)
        self.metrics.discoveries += max(0, after - before)
        self.metrics.record("sense", position=self.robot.position, discovered=max(0, after - before))

    def run(self, max_steps: int = 250) -> MissionMetrics:
        if max_steps <= 0:
            raise ValueError("max_steps must be positive.")

        self.sense()
        if self.base_position is None:
            self.base_position = self.robot.position

        returning = False
        for _ in range(max_steps):
            if self.robot.battery <= self.battery_reserve and self.robot.position != self.base_position:
                returning = True
                self.metrics.record("mode_change", mode="RETURN_TO_BASE")

            if returning:
                path = _shortest_known_path(self.known, self.robot.position, self.base_position)
                if path is None:
                    self.metrics.safety_stops += 1
                    self.metrics.record("return_failed", base=self.base_position)
                    break
                if len(path) == 1:
                    self.metrics.record("mission_complete", reason="returned_to_base")
                    break
                target = None
                vantage = self.base_position
            else:
                candidate = self.frontier_selector(self.known, self.robot.position)
                if candidate is None:
                    self.metrics.record("mission_complete", reason="no_reachable_frontier")
                    break
                target = candidate.frontier
                vantage = candidate.vantage
                self.metrics.record("decision", frontier=target, vantage=vantage, score=candidate.score, information_gain=candidate.information_gain)
                path = None
            if path is None:
                started = perf_counter()
                path = _shortest_known_path(self.known, self.robot.position, vantage)
                elapsed = perf_counter() - started
            else:
                started = perf_counter()
                elapsed = perf_counter() - started
            self.metrics.record_plan(elapsed * 1000.0)

            if path is None:
                self.metrics.safety_stops += 1
                self.metrics.record("replan_failed", target=vantage)
                break

            next_position = path[1] if len(path) > 1 else path[0]
            if next_position not in self.known.known_free:
                self.metrics.safety_stops += 1
                self.metrics.record("safety_stop", position=next_position)
                self.sense()
                continue

            self.robot = self.robot.moved_to(next_position)
            self.metrics.steps += 1
            self.metrics.record("move", position=next_position, frontier=target)
            self.sense()
            if returning and self.robot.position == self.base_position:
                self.metrics.record("mission_complete", reason="returned_to_base")
                break

        return self.metrics
