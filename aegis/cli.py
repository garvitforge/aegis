"""Command-line entry point for a small AEGIS planning demo."""

from .grid import GridMap
from .planning import astar


def main() -> None:
    grid = GridMap(
        width=12,
        height=8,
        obstacles=frozenset(
            {
                (3, 0), (3, 1), (3, 2),
                (6, 3), (7, 3), (8, 3),
                (9, 5), (9, 6),
            }
        ),
    )

    start = (0, 0)
    goal = (11, 7)
    path = astar(grid, start, goal)

    print(f"AEGIS A* demo: {start} -> {goal}")
    print(f"Path length: {len(path) - 1} moves")
    print("Path:")
    print(" -> ".join(map(str, path)))


if __name__ == "__main__":
    main()
