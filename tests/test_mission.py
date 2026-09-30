from aegis.grid import GridMap
from aegis.mapping import OccupancyMap
from aegis.metrics import MissionMetrics
from aegis.mission import Mission
from aegis.sensors import FourWayRangeSensor
from aegis.state import RobotState


def test_mission_collects_real_telemetry() -> None:
    truth = GridMap(
        8,
        6,
        frozenset({(4, 1), (4, 2), (4, 3), (2, 4)}),
    )
    mission = Mission(
        truth=truth,
        robot=RobotState((1, 1)),
        known=OccupancyMap(8, 6, set(), set()),
        sensor=FourWayRangeSensor(2),
        metrics=MissionMetrics(),
    )

    metrics = mission.run(40)

    assert metrics.steps > 0
    assert metrics.replans > 0
    assert metrics.discoveries > 0
    assert metrics.events
