# AEGIS

**Autonomous Emergency Ground Intelligence System**

AEGIS is an experimental robotics platform for autonomous exploration and emergency-response scenarios.

The long-term goal is to combine:

**Perception → Sensor Fusion → Mapping → Planning → Decision Making → Control → Telemetry**

This repository starts with simulation and algorithmic foundations before hardware deployment.

## Current status

**v0.5 — Decision-aware autonomous exploration**

Implemented:
- Grid-world environment
- Occupancy/obstacle representation
- 4-connected A* path planning
- Robot state and battery model
- Unknown-space frontier detection
- Nearest reachable frontier selection
- Deterministic unit tests
- Automated CI testing
- Deterministic range-sensor simulation
- Partial-observability occupancy map
- Closed-loop sense → map → plan → move → sense exploration
- Planning restricted to discovered free space
- Information-gain frontier scoring with deterministic tie-breaking
- Battery-aware return-to-base mission mode
- Mission decision telemetry and safety-stop tracking
- Deterministic multi-scenario benchmark suite

Planned:
- Dynamic environment simulation
- Richer frontier scoring and risk models
- Real-time telemetry dashboard
- Computer vision
- Hardware abstraction layer
- Physical robot integration

## Architecture

```
Sensors / Simulator
        ↓
   Perception
        ↓
   Sensor Fusion
        ↓
 Environment Model
        ↓
 Decision / Planner
        ↓
 Motion Controller
        ↓
 Robot / Simulator
        ↓
 Telemetry & Logging
```

## Engineering principles

- Reproducible experiments
- Small testable components
- Measurable performance
- Hardware/software separation
- Fail-safe behavior
- Documented assumptions

## Project status

This is an actively developed student engineering project. Features are marked as implemented only after they exist in the repository and are tested.
