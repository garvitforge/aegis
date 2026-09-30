# AEGIS

**Autonomous Emergency Ground Intelligence System**

AEGIS is an experimental robotics platform for autonomous exploration and emergency-response scenarios.

The long-term goal is to combine:

**Perception → Sensor Fusion → Mapping → Planning → Decision Making → Control → Telemetry**

This repository starts with simulation and algorithmic foundations before hardware deployment.

## Current status

**v0.2 — State & exploration foundation**

Implemented:
- Grid-world environment
- Occupancy/obstacle representation
- 4-connected A* path planning
- Robot state and battery model
- Unknown-space frontier detection
- Nearest reachable frontier selection
- Deterministic unit tests
- Automated CI testing

Planned:
- Incremental sensor simulation
- Occupancy-grid updates
- Dynamic obstacles
- Frontier scoring / information gain
- Return-to-base logic
- Real-time telemetry
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
