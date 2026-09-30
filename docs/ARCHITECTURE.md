# AEGIS Architecture

## Design goal

AEGIS is being developed as a layered autonomous system. Each layer should be testable independently before being coupled to hardware.

## Layers

### 1. Perception
Consumes camera and sensor measurements.

Examples:
- RGB/depth camera
- Time-of-flight distance sensors
- Wheel encoders
- IMU
- Environmental sensors

### 2. Sensor Fusion
Combines noisy measurements into a consistent estimate of robot state and surroundings.

### 3. Environment Model
Maintains the robot's internal representation of obstacles and explored space.

The first implementation uses a deterministic grid representation.

### 4. Planning
Chooses a safe route toward a target or exploration frontier.

The first implementation uses A* with Manhattan distance on a 4-connected grid.

### 5. Control
Converts a planned path into motion commands while respecting the robot's physical limits.

This layer is intentionally not coupled to the simulator yet.

### 6. Telemetry
Records state, decisions and performance so experiments can be reproduced and compared.

## Why these boundaries matter

A robotics project becomes difficult to debug when sensing, planning and motor control are mixed together. AEGIS keeps those responsibilities separate so that an algorithm can be tested in simulation before it controls physical hardware.
