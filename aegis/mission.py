"""Mission-level autonomy and telemetry for AEGIS."""

from dataclasses import dataclass
from time import perf_counter

from .autonomy import _frontier_vantage, _shortest_known_path
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

        for _ in range(max_steps):
            target = _frontier_vantage(self.known, self.robot.position)
            if target is None:
                self.metrics.record("mission_complete", reason="no_reachable_frontier")
                break

            frontier, vantage = target
            started = perf_counter()
            path = _shortest_known_path(self.known, self.robot.position, vantage)
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
            self.metrics.record("move", position=next_position, frontier=frontier)
            self.sense()

        return self.metrics
