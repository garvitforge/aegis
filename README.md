# AEGIS

**Autonomous Emergency Ground Intelligence System**  
*Simulation-first research prototype for autonomous exploration, mapping, and return-to-base planning.*

[![Tests](https://github.com/garvitforge/aegis/actions/workflows/tests.yml/badge.svg)](https://github.com/garvitforge/aegis/actions/workflows/tests.yml)

AEGIS explores how a robot can navigate a grid while seeing only local sensor observations, build an occupancy map, select useful exploration frontiers, and make battery-aware return decisions. It is a software simulation—not a certified rescue system or a physical robot.

## Current milestone

**v0.7.0 — Reproducible benchmark workflow**

- Grid-world model with obstacle and boundary validation
- A* path planning over known traversable space
- Deterministic four-direction range sensor and occupancy mapping
- Frontier-based exploration with local information-gain scoring
- BFS distance maps for efficient reachable-frontier scoring
- Closed-loop sense → map → decide → plan → move → sense mission loop
- Battery-aware return-to-base mode using estimated route length
- Mission event telemetry and planning-time measurements
- JSON benchmark output for repeatable comparison and external plotting
- Automated tests on Python 3.10–3.13 via GitHub Actions

## Quick start

Requires Python 3.10 or newer.

```bash
python -m pip install -e ".[dev]"
pytest -q
aegis demo
aegis benchmark
aegis benchmark --output reports/benchmark.json
python -m aegis.mission_demo
python -m aegis.closed_loop_demo
```

Windows users can use the Python launcher if needed:

```bat
py -3.12 -m pip install -e ".[dev]"
py -3.12 -m pytest -q
```

## How it works

1. **Sense:** the simulated range sensor observes nearby free cells and obstacles.
2. **Map:** observations update the robot's partial occupancy map.
3. **Decide:** reachable frontier approaches are scored using estimated information gain and travel distance.
4. **Plan:** pathfinding uses discovered free cells rather than hidden map truth.
5. **Move:** the simulated robot advances one cell and pays a configurable battery cost.
6. **Return:** when estimated route cost plus reserve approaches the remaining battery, the mission switches to base-return mode.
7. **Measure:** events, discoveries, steps, safety stops, and planning latency are recorded.

## Benchmarks

`aegis benchmark` runs the bundled deterministic corridor and split-room scenarios. Use `--output` to save a JSON report. Coverage is the fraction of traversable map cells discovered by the mission. Planning time is measured wall-clock time and can vary by machine and run; compare deterministic outcomes separately from timing.

The benchmark is intentionally small and is not evidence of real-world rescue performance. See [experiment notes](docs/EXPERIMENTS.md) for interpretation and extension ideas.

## Project structure

- `aegis/grid.py` — grid world and coordinate types
- `aegis/planning.py`, `aegis/autonomy.py`, `aegis/distance.py` — path planning and known-space reachability
- `aegis/sensors.py`, `aegis/mapping.py` — sensing and partial map
- `aegis/exploration.py`, `aegis/decision.py` — frontier discovery and target scoring
- `aegis/mission.py`, `aegis/state.py`, `aegis/metrics.py` — mission loop, robot state, telemetry
- `aegis/benchmark.py`, `aegis/cli.py` — scenarios, measurements, command-line interface
- `tests/` — unit and regression tests

## Limitations and safety

- The environment, sensing, and motion are idealized and deterministic.
- There is no physical hardware integration, camera perception, SLAM, dynamic-obstacle handling, sensor noise, wheel slip, or communications stack.
- Battery use is a simplified per-cell estimate. Return-to-base logic is a simulation policy, not a guaranteed safety mechanism.
- The local frontier score is a heuristic, not a probabilistic information-theory model.
- No real-world performance, rescue capability, or safety certification is claimed.

## Roadmap

- Add seeded randomized maps and statistical benchmark summaries
- Compare frontier strategies across identical scenarios
- Model sensor noise, dynamic obstacles, and uncertain movement
- Add visual map/telemetry playback
- Define a hardware abstraction layer only after simulation tests are robust

Contributions and reproducible bug reports are welcome. AEGIS prioritizes testable behavior, measurable results, and honest statements about what is implemented.
