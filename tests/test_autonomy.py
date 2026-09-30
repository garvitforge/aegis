from aegis.autonomy import ExplorationSimulator, explore
from aegis.grid import GridMap
from aegis.mapping import OccupancyMap
from aegis.sensors import FourWayRangeSensor
from aegis.state import RobotState


def test_controller_never_moves_into_unknown_space() -> None:
    truth = GridMap(
        width=8,
        height=6,
        obstacles=frozenset({(4, 1), (4, 2), (4, 3), (2, 4)}),
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
        sensor=FourWayRangeSensor(max_range=2),
    )

    explore(simulator)

    assert simulator.robot.position in simulator.known.known_free
    assert simulator.robot.position not in simulator.known.known_obstacles


def test_closed_loop_discovers_real_obstacles() -> None:
    truth = GridMap(
        width=6,
        height=5,
        obstacles=frozenset({(3, 2), (3, 3)}),
    )
    simulator = ExplorationSimulator(
        truth=truth,
        robot=RobotState(position=(1, 2)),
        known=OccupancyMap(
            width=truth.width,
            height=truth.height,
            known_free=set(),
            known_obstacles=set(),
        ),
        sensor=FourWayRangeSensor(max_range=2),
    )

    explore(simulator)

    assert (3, 2) in simulator.known.known_obstacles
    assert (3, 3) in simulator.known.known_obstacles
