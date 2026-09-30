import dataclasses

from aegis.decision import nearest_frontier_candidate
from aegis.grid import GridMap
from aegis.mapping import OccupancyMap
from aegis.metrics import MissionMetrics
from aegis.mission import Mission
from aegis.sensors import FourWayRangeSensor
from aegis.state import RobotState


def _mission(**kwargs) -> Mission:
    truth = GridMap(8, 6, frozenset({(4, 1), (4, 2), (4, 3)}))
    return Mission(
        truth=truth,
        robot=RobotState((1, 1)),
        known=OccupancyMap(8, 6, set(), set()),
        sensor=FourWayRangeSensor(2),
        metrics=MissionMetrics(),
        **kwargs,
    )


def test_mission_fields_are_declared_once() -> None:
    names = [f.name for f in dataclasses.fields(Mission)]
    assert len(names) == len(set(names))


def test_mission_accepts_a_custom_frontier_selector() -> None:
    mission = _mission(frontier_selector=nearest_frontier_candidate)
    metrics = mission.run(200)
    assert metrics.steps > 0
    assert any(e["event"] == "mission_complete" for e in metrics.events)


def test_low_battery_triggers_return_to_base() -> None:
    mission = _mission(battery_reserve=20.0)
    mission.robot = RobotState((1, 1), battery=20.3)
    metrics = mission.run(200)
    assert any(e.get("mode") == "RETURN_TO_BASE" for e in metrics.events)
    assert mission.robot.position == mission.base_position
