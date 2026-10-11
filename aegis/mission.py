"""Mission-level autonomy, battery-aware return, and telemetry for AEGIS."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from .autonomy import _shortest_known_path
from .decision import FrontierCandidate, best_frontier
from .grid import GridMap, Position
from .mapping import OccupancyMap
from .metrics import MissionMetrics
from .sensors import FourWayRangeSensor
from .state import RobotState


@dataclass
class Mission:
    truth: GridMap
    robot: RobotState
    known: OccupancyMap
    sensor: FourWayRangeSensor
    metrics: MissionMetrics
    battery_reserve: float = 20.0
    base_position: Position | None = None
    battery_cost_per_move: float = 0.1
    frontier_selector: Callable[
        [OccupancyMap, Position], FrontierCandidate | None
    ] = best_frontier

    def __post_init__(self) -> None:
        if not 0.0 <= self.battery_reserve <= 100.0:
            raise ValueError("battery_reserve must be between 0 and 100.")
        if self.battery_cost_per_move < 0.0:
            raise ValueError("battery_cost_per_move cannot be negative.")

    def sense(self) -> None:
        before = len(self.known.known_free) + len(self.known.known_obstacles)
        observation = self.sensor.sense(self.truth, self.robot.position)
        self.known.update(set(observation.free_cells), set(observation.obstacle_cells))
        after = len(self.known.known_free) + len(self.known.known_obstacles)
        discovered = max(0, after - before)
        self.metrics.discoveries += discovered
        self.metrics.record("sense", position=self.robot.position, discovered=discovered)

    def _plan(self, goal: Position) -> tuple[list[Position] | None, float]:
        started = perf_counter()
        path = _shortest_known_path(self.known, self.robot.position, goal)
        elapsed_ms = (perf_counter() - started) * 1000.0
        self.metrics.record_plan(elapsed_ms)
        return path, elapsed_ms

    def run(self, max_steps: int = 250) -> MissionMetrics:
        if max_steps <= 0:
            raise ValueError("max_steps must be positive.")

        self.sense()
        if self.base_position is None:
            self.base_position = self.robot.position
        returning = False

        for _ in range(max_steps):
            base_path: list[Position] | None = None
            if self.robot.position != self.base_position:
                base_path, _ = self._plan(self.base_position)

            # Reserve enough charge for the known shortest route home, plus a
            # configurable safety reserve. If no route is known, fail safely.
            if self.robot.position != self.base_position:
                if base_path is None:
                    if self.robot.battery <= self.battery_reserve:
                        self.metrics.safety_stops += 1
                        self.metrics.record("return_failed", base=self.base_position)
                        break
                else:
                    required = self.battery_reserve + max(
                        0, len(base_path) - 1
                    ) * self.battery_cost_per_move
                    if self.robot.battery <= required:
                        if not returning:
                            self.metrics.record(
                                "mode_change",
                                mode="RETURN_TO_BASE",
                                battery=self.robot.battery,
                                estimated_return_cost=(
                                    max(0, len(base_path) - 1) * self.battery_cost_per_move
                                ),
                            )
                        returning = True

            if returning:
                path = base_path
                target = None
                vantage = self.base_position
                if path is None:
                    self.metrics.safety_stops += 1
                    self.metrics.record("return_failed", base=self.base_position)
                    break
                if len(path) == 1:
                    self.metrics.record("mission_complete", reason="returned_to_base")
                    break
            else:
                candidate = self.frontier_selector(self.known, self.robot.position)
                if candidate is None:
                    self.metrics.record("mission_complete", reason="no_reachable_frontier")
                    break
                target = candidate.frontier
                vantage = candidate.vantage
                self.metrics.record(
                    "decision",
                    frontier=target,
                    vantage=vantage,
                    score=candidate.score,
                    information_gain=candidate.information_gain,
                )
                path, _ = self._plan(vantage)
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

            self.robot = self.robot.moved_to(
                next_position, battery_cost=self.battery_cost_per_move
            )
            self.metrics.steps += 1
            self.metrics.record("move", position=next_position, frontier=target)
            self.sense()

            if returning and self.robot.position == self.base_position:
                self.metrics.record("mission_complete", reason="returned_to_base")
                break

        return self.metrics
