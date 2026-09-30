from aegis.mapping import OccupancyMap
from aegis.render import render_ascii


def test_ascii_render_marks_robot_base_obstacle_free_and_unknown() -> None:
    known = OccupancyMap(4, 2, {(0, 0), (1, 0)}, {(2, 0)})
    text = render_ascii(known, robot=(1, 0), base=(0, 0))
    rows = text.split("\n")
    assert rows[0] == "BR# "
    assert rows[1] == "    "
    assert len(rows) == 2
