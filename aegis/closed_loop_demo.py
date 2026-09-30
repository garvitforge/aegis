"""Run the AEGIS partial-observability exploration demo."""

from .autonomy import ExplorationSimulator, explore
from .grid import GridMap
from .mapping import OccupancyMap
from .sensors import FourWayRangeSensor
from .state import RobotState


def run_demo() -> None:
    truth = GridMap(
        width=12,
        height=8,
        obstacles=frozenset(
            {
                (4, 1), (4, 2), (4, 3), (4, 4),
                (7, 5), (8, 5), (9, 5),
                (2, 6), (3, 6),
            }
        ),
    )

    simulator = ExplorationSimulator(
        truth=truth,
        robot=RobotState(position=(1, 1)),
        known=OccupancyMap(
            width=truth.width,
            height=truth.height,
            known_free=set(),
            known_obstacles=set(),
        ),
        sensor=FourWayRangeSensor(max_range=3),
    )

    iterations = explore(simulator)

    print("AEGIS closed-loop exploration")
    print(f"Iterations: {iterations}")
    print(f"Final position: {simulator.robot.position}")
    print(f"Battery: {simulator.robot.battery:.1f}%")
    print(f"Discovered free cells: {len(simulator.known.known_free)}")
    print(f"Discovered obstacles: {len(simulator.known.known_obstacles)}")
    print("Planner used hidden truth map: NO")


if __name__ == "__main__":
    run_demo()
