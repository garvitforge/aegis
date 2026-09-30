"""Run a measurable AEGIS autonomy mission."""

from .grid import GridMap
from .mapping import OccupancyMap
from .metrics import MissionMetrics
from .mission import Mission
from .sensors import FourWayRangeSensor
from .state import RobotState


def run_demo() -> None:
    truth = GridMap(
        14,
        9,
        frozenset({
            (4, 1), (4, 2), (4, 3), (4, 4),
            (8, 6), (9, 6), (10, 6),
            (2, 7), (3, 7), (4, 7),
        }),
    )

    mission = Mission(
        truth=truth,
        robot=RobotState((1, 1)),
        known=OccupancyMap(14, 9, set(), set()),
        sensor=FourWayRangeSensor(3),
        metrics=MissionMetrics(),
    )

    metrics = mission.run(80)

    print("=== AEGIS Mission Report ===")
    print(f"Steps: {metrics.steps}")
    print(f"Replans: {metrics.replans}")
    print(f"Discovered cells: {metrics.discoveries}")
    print(f"Average planning time: {metrics.average_planning_time_ms:.3f} ms")
    print(f"Safety stops: {metrics.safety_stops}")
    print(f"Final position: {mission.robot.position}")


if __name__ == "__main__":
    run_demo()
