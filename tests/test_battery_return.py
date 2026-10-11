from aegis.grid import GridMap
from aegis.mapping import OccupancyMap
from aegis.metrics import MissionMetrics
from aegis.mission import Mission
from aegis.sensors import FourWayRangeSensor
from aegis.state import RobotState


def test_low_battery_returns_to_explicit_base() -> None:
    truth = GridMap(5, 3)
    known = OccupancyMap(
        5, 3, {(x, y) for x in range(5) for y in range(3)}, set()
    )
    mission = Mission(
        truth=truth,
        robot=RobotState((2, 1), battery=20.1),
        known=known,
        sensor=FourWayRangeSensor(2),
        metrics=MissionMetrics(),
        base_position=(0, 1),
    )

    metrics = mission.run(20)

    assert mission.robot.position == (0, 1)
    assert any(
        event.get("mode") == "RETURN_TO_BASE"
        for event in metrics.events
    )
