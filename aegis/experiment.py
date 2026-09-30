"""Reproducible strategy comparison on seeded random maps.

Compares three exploration strategies under identical conditions:

* ``random_walk``: move to a random known-free neighbour (no planning).
* ``nearest``: A*-free BFS to the closest frontier (distance only).
* ``scored``: AEGIS frontier scoring, ``2 * information_gain - distance``.

All runs are deterministic for a given base seed.
"""

import random
from dataclasses import dataclass
from statistics import mean, median

from .decision import best_frontier, nearest_frontier_candidate
from .generators import GENERATORS
from .grid import GridMap, Position
from .mapping import OccupancyMap
from .metrics import MissionMetrics
from .mission import Mission
from .sensors import FourWayRangeSensor
from .state import RobotState
from .trace import coverage_trace, reachable_free_count

STRATEGIES = ("random_walk", "nearest", "scored")
CHECKPOINTS = (50, 100, 200)


@dataclass(frozen=True)
class RunResult:
    strategy: str
    map_index: int
    moves: int
    completed: bool
    trace: tuple[float, ...]
    positions: tuple[Position, ...] = ()

    @property
    def final_coverage(self) -> float:
        return self.trace[-1]

    def coverage_at(self, step: int) -> float:
        return self.trace[min(step, len(self.trace) - 1)]

    def moves_to_coverage(self, target: float) -> int | None:
        for index, value in enumerate(self.trace):
            if value >= target:
                return index
        return None


def run_frontier_strategy(
    strategy: str,
    truth: GridMap,
    start: Position,
    sensor_range: int,
    max_moves: int,
    map_index: int = 0,
) -> RunResult:
    selector = {"nearest": nearest_frontier_candidate, "scored": best_frontier}[strategy]
    mission = Mission(
        truth=truth,
        robot=RobotState(start),
        known=OccupancyMap(truth.width, truth.height, set(), set()),
        sensor=FourWayRangeSensor(sensor_range),
        metrics=MissionMetrics(),
        battery_reserve=0.0,  # isolate exploration quality from battery policy
        frontier_selector=selector,
    )
    metrics = mission.run(max_moves)
    positions = [e["position"] for e in metrics.events if e["event"] == "move"]
    completed = any(
        e["event"] == "mission_complete" and e.get("reason") == "no_reachable_frontier"
        for e in metrics.events
    )
    trace = coverage_trace(truth, start, positions, sensor_range)
    return RunResult(strategy, map_index, metrics.steps, completed, tuple(trace), tuple(positions))


def run_random_walk(
    truth: GridMap,
    start: Position,
    sensor_range: int,
    max_moves: int,
    seed: int,
    map_index: int = 0,
) -> RunResult:
    rng = random.Random(seed)
    sensor = FourWayRangeSensor(sensor_range)
    known = OccupancyMap(truth.width, truth.height, set(), set())
    total = reachable_free_count(truth, start)

    def scan(pos: Position) -> None:
        obs = sensor.sense(truth, pos)
        known.update(set(obs.free_cells), set(obs.obstacle_cells))

    position = start
    scan(position)
    visited: list[Position] = []
    trace = [len(known.known_free) / total]
    completed = trace[-1] >= 1.0
    moves = 0

    while moves < max_moves and not completed:
        x, y = position
        options = [
            nb
            for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
            if nb in known.known_free
        ]
        if not options:
            break
        position = options[int(rng.random() * len(options))]
        visited.append(position)
        moves += 1
        scan(position)
        trace.append(len(known.known_free) / total)
        completed = trace[-1] >= 1.0

    return RunResult("random_walk", map_index, moves, completed, tuple(trace), tuple(visited))


@dataclass(frozen=True)
class StrategySummary:
    strategy: str
    maps: int
    completion_rate: float
    mean_moves_to_complete: float | None
    median_moves_to_complete: float | None
    mean_moves_to_90: float | None
    reached_90_rate: float
    mean_coverage_at: dict[int, float]


def summarize(strategy: str, results: list[RunResult]) -> StrategySummary:
    done = [r.moves for r in results if r.completed]
    to90 = [m for r in results if (m := r.moves_to_coverage(0.9)) is not None]
    return StrategySummary(
        strategy=strategy,
        maps=len(results),
        completion_rate=len(done) / len(results),
        mean_moves_to_complete=mean(done) if done else None,
        median_moves_to_complete=median(done) if done else None,
        mean_moves_to_90=mean(to90) if to90 else None,
        reached_90_rate=len(to90) / len(results),
        mean_coverage_at={k: mean(r.coverage_at(k) for r in results) for k in CHECKPOINTS},
    )


def mean_curve(results: list[RunResult], length: int) -> list[float]:
    return [mean(r.coverage_at(k) for r in results) for k in range(length + 1)]


@dataclass(frozen=True)
class ExperimentReport:
    kind: str
    maps: int
    size: int
    density: float
    sensor_range: int
    seed: int
    max_moves: int
    summaries: dict[str, StrategySummary]
    curves: dict[str, list[float]]


def make_map(kind: str, size: int, density: float, seed: int) -> tuple[GridMap, Position]:
    if kind == "random":
        return GENERATORS["random"](size, size, density, seed)
    if kind == "rooms":
        return GENERATORS["rooms"](size, size, 6, seed)
    raise ValueError(f"Unknown map kind: {kind}")


def run_experiment(
    maps: int = 50,
    size: int = 20,
    density: float = 0.2,
    sensor_range: int = 3,
    seed: int = 0,
    kind: str = "random",
    max_moves: int | None = None,
    curve_length: int = 300,
) -> ExperimentReport:
    if maps <= 0:
        raise ValueError("maps must be positive.")
    budget = max_moves if max_moves is not None else min(2 * size * size, 900)

    results: dict[str, list[RunResult]] = {name: [] for name in STRATEGIES}
    for index in range(maps):
        truth, start = make_map(kind, size, density, seed + index)
        results["random_walk"].append(
            run_random_walk(truth, start, sensor_range, budget, seed * 1000 + index, index)
        )
        for name in ("nearest", "scored"):
            results[name].append(
                run_frontier_strategy(name, truth, start, sensor_range, budget, index)
            )

    return ExperimentReport(
        kind=kind,
        maps=maps,
        size=size,
        density=density,
        sensor_range=sensor_range,
        seed=seed,
        max_moves=budget,
        summaries={name: summarize(name, rs) for name, rs in results.items()},
        curves={name: mean_curve(rs, curve_length) for name, rs in results.items()},
    )


def format_report(report: ExperimentReport) -> str:
    def fmt(value: float | None, digits: int = 1) -> str:
        return "n/a" if value is None else f"{value:.{digits}f}"

    header = (
        f"kind={report.kind} maps={report.maps} size={report.size}x{report.size} "
        f"density={report.density} sensor_range={report.sensor_range} "
        f"seed={report.seed} budget={report.max_moves} moves"
    )
    cols = "| strategy | completed | moves to finish (mean) | moves to 90% (mean, share of maps that got there) | " + " | ".join(
        f"coverage @{k}" for k in CHECKPOINTS
    ) + " |"
    sep = "|" + "---|" * (4 + len(CHECKPOINTS))
    lines = [header, "", cols, sep]
    for name in STRATEGIES:
        s = report.summaries[name]
        cov = " | ".join(f"{s.mean_coverage_at[k] * 100:.1f}%" for k in CHECKPOINTS)
        lines.append(
            f"| {name} | {s.completion_rate * 100:.0f}% | {fmt(s.mean_moves_to_complete)} | "
            f"{fmt(s.mean_moves_to_90)} ({s.reached_90_rate * 100:.0f}% reached) | {cov} |"
        )
    return "\n".join(lines)
