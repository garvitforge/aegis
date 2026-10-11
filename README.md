# AEGIS

**Autonomous Emergency Ground Intelligence System**

AEGIS is a simulation-first robotics project exploring how a robot can navigate a partially known grid, map its surroundings, choose exploration targets, and return to base safely. It is an algorithmic prototype—not yet a physical rescue robot.

## Current status

**v0.6.0 — Faster frontier decisions and battery-aware return**

Implemented:
- Grid-world environment and 4-connected A* path planning
- Robot state, battery model, and deterministic four-direction range sensing
- Partial-observability occupancy mapping
- Frontier detection and deterministic information-gain scoring
- BFS distance maps to evaluate many reachable frontier approaches from one traversal
- Reference A*-based frontier candidate implementation for differential testing
- Closed-loop sense → map → plan → move → sense exploration
- Return-to-base decisions that account for estimated path length and battery cost
- Mission telemetry, planning-time measurements, and safety-stop events
- Automated tests and GitHub Actions CI

## Quick start

Python 3.10 or newer is required.

```bash
python -m pip install -e ".[dev]"
pytest -q
aegis
python -m aegis.mission_demo
```

On Windows, use `py -3.12 -m pip install -e ".[dev]"` if the `python` command is not available but the Python launcher is installed.

## Important limitations

- This is a deterministic grid simulation, not a real robot.
- The sensor and motion model are idealized; sensor noise, wheel slip, dynamic obstacles, and physical hardware interfaces are not implemented.
- Return planning estimates battery use from grid moves and a configured per-move cost. It is not a certified safety guarantee.
- The frontier information-gain score is a simple local heuristic, not an entropy-based model.

## Roadmap

- Hybrid frontier strategy and broader reproducible benchmark suite
- Dynamic obstacles and sensor-noise experiments
- Better energy modelling and return-to-base risk handling
- Telemetry dashboard
- Hardware abstraction, computer vision, and physical robot integration

## Engineering principles

- Reproducible, deterministic tests
- Small, testable components
- Measurable planning performance
- Planning restricted to discovered free space
- Explicit assumptions and honest scope

AEGIS is actively developed. Features are described as implemented only when code and tests support them.
