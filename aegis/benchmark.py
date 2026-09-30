"""Deterministic benchmark utilities for AEGIS missions."""

from dataclasses import dataclass

from .grid import GridMap
from .mapping import OccupancyMap
from .metrics import MissionMetrics
from .mission import Mission
from .sensors import FourWayRangeSensor
from .state import RobotState


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    steps: int
    replans: int
    discoveries: int
    coverage: float
    average_planning_time_ms: float
    safety_stops: int
    final_battery: float


def run_scenario(name: str, truth: GridMap, start: tuple[int, int], sensor_range: int = 2) -> BenchmarkResult:
    mission = Mission(
        truth=truth,
        robot=RobotState(start),
        known=OccupancyMap(truth.width, truth.height, set(), set()),
        sensor=FourWayRangeSensor(sensor_range),
        metrics=MissionMetrics(),
    )
    metrics = mission.run()
    traversable = truth.width * truth.height - len(truth.obstacles)
    known_traversable = len(mission.known.known_free)
    coverage = known_traversable / traversable if traversable else 0.0
    return BenchmarkResult(
        name=name,
        steps=metrics.steps,
        replans=metrics.replans,
        discoveries=metrics.discoveries,
        coverage=coverage,
        average_planning_time_ms=metrics.average_planning_time_ms,
        safety_stops=metrics.safety_stops,
        final_battery=mission.robot.battery,
    )


def default_scenarios() -> dict[str, tuple[GridMap, tuple[int, int]]]:
    return {
        "corridor": (GridMap(8, 5, frozenset({(3, 1), (3, 2), (3, 3)})), (1, 2)),
        "split_room": (GridMap(10, 7, frozenset({(4, y) for y in range(1, 6)} | {(7, 2), (7, 3), (7, 4)})), (1, 1)),
    }


def run_default_benchmark() -> list[BenchmarkResult]:
    return [run_scenario(name, grid, start) for name, (grid, start) in default_scenarios().items()]
