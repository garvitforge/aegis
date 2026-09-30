import pytest

from aegis.state import Heading, RobotState


def test_default_robot_state() -> None:
    state = RobotState((2, 3))

    assert state.position == (2, 3)
    assert state.heading is Heading.NORTH
    assert state.battery == 100.0


def test_move_returns_new_state_and_consumes_battery() -> None:
    state = RobotState((0, 0), battery=80.0)
    moved = state.moved_to((1, 0), battery_cost=2.5)

    assert state.position == (0, 0)
    assert moved.position == (1, 0)
    assert moved.battery == 77.5


def test_battery_range_is_validated() -> None:
    with pytest.raises(ValueError):
        RobotState((0, 0), battery=101.0)
