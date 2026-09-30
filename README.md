# AEGIS

**Autonomous Emergency Ground Intelligence System**

AEGIS is an experimental robotics platform for autonomous exploration and emergency-response scenarios.

The long-term goal is to combine:

**Perception → Sensor Fusion → Mapping → Planning → Decision Making → Control → Telemetry**

This repository starts with simulation and algorithmic foundations before hardware deployment.

## Current status

**v0.1 — Simulation foundation**

Implemented:
- Grid-world environment
- Occupancy/obstacle representation
- 4-connected A* path planning
- Deterministic path validation
- Unit tests for the core planner

Planned:
- Robot state model
- Sensor simulation
- Exploration and frontier selection
- Dynamic obstacles
- Real-time telemetry
- Computer vision
- Hardware abstraction layer
- Physical robot integration

## Why simulation first?

Autonomous systems are easier to debug when perception, planning and control can be tested independently. AEGIS therefore treats simulation as an engineering tool, not just a visual demo.

## Architecture

```text
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
