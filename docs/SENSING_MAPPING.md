# Sensing & Mapping

AEGIS uses a deliberately simple simulated sensor before introducing real hardware.

## Observation model

The FourWayRangeSensor scans north, south, east, and west up to a fixed range.

For each direction it reports:
- free cells until an obstacle or map boundary
- the first obstacle encountered
- no information beyond that obstacle

This makes the simulator deterministic and easy to test.

## Partial observability

The simulator contains a hidden GridMap, but the controller does not receive that map.

Instead:
1. The sensor observes the robot's current position.
2. OccupancyMap merges the observation.
3. Frontier cells are identified at the boundary between known and unknown space.
4. The controller chooses a reachable frontier.
5. A* plans only through cells already known to be free.
6. The robot moves to a known-free vantage point.
7. A new sensor scan reveals more of the environment.

Unknown cells are therefore treated as unsafe for planning until they are observed.

## Why this matters

This separation is the foundation for later hardware integration. A real robot will replace the deterministic simulator sensor with camera, ToF, lidar, encoder, or other observations without changing the high-level exploration concept.