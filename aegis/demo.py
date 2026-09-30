"""Run a small end-to-end AEGIS exploration demonstration."""

from .exploration import frontier_cells, nearest_frontier
from .grid import GridMap
from .state import RobotState


def run_demo() -> None:
    grid = GridMap(
        width=10,
        height=7,
        obstacles=frozenset(
            {
                (4, 1), (4, 2), (4, 3),
                (7, 4), (7, 5),
            }
        ),
    )

    robot = RobotState(position=(1, 1))
    known_free = {robot.position}
    known_obstacles = {(4, 1)}

    frontiers = frontier_cells(
        known_free=known_free,
        known_obstacles=known_obstacles,
        width=grid.width,
        height=grid.height,
    )

    target = nearest_frontier(grid, robot.position, frontiers)

    print("AEGIS exploration demo")
    print(f"Robot position: {robot.position}")
    print(f"Battery: {robot.battery:.1f}%")
    print(f"Frontier cells: {sorted(frontiers)}")
    print(f"Selected frontier: {target}")


if __name__ == "__main__":
    run_demo()
