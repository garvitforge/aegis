"""Command-line entry point for AEGIS.

    aegis                      run a small A* planning demo
    aegis benchmark            compare exploration strategies on seeded maps
    aegis replay               run one mission and save an animated GIF
"""

import argparse
import sys

from .experiment import format_report, make_map, run_experiment, run_frontier_strategy
from .grid import GridMap
from .planning import astar
from .render import render_ascii
from .trace import replay_states


def _astar_demo() -> None:
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


def _add_map_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--kind", choices=("random", "rooms"), default="random")
    p.add_argument("--size", type=int, default=20)
    p.add_argument("--density", type=float, default=0.2)
    p.add_argument("--sensor-range", type=int, default=3)
    p.add_argument("--seed", type=int, default=0)


def _benchmark(args: argparse.Namespace) -> None:
    report = run_experiment(
        maps=args.maps,
        size=args.size,
        density=args.density,
        sensor_range=args.sensor_range,
        seed=args.seed,
        kind=args.kind,
    )
    print(format_report(report))
    if args.chart:
        from .viz import save_coverage_chart

        save_coverage_chart(report.curves, args.chart)
        print(f"\nchart written to {args.chart}")


def _replay(args: argparse.Namespace) -> None:
    truth, start = make_map(args.kind, args.size, args.density, args.seed)
    result = run_frontier_strategy("scored", truth, start, args.sensor_range, 900)
    positions = list(result.positions)

    print(f"mission finished: {result.moves} moves, final coverage {result.final_coverage * 100:.1f}%")
    if args.ascii or not args.out:
        *_, (robot, known) = replay_states(truth, start, positions, args.sensor_range)
        print(render_ascii(known, robot, start))
    if args.out:
        from .viz import save_replay_gif

        frames = save_replay_gif(truth, start, positions, args.sensor_range, args.out)
        print(f"wrote {frames} frames to {args.out}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="aegis", description="AEGIS exploration simulator")
    sub = parser.add_subparsers(dest="command")

    bench = sub.add_parser("benchmark", help="compare exploration strategies on seeded maps")
    _add_map_args(bench)
    bench.add_argument("--maps", type=int, default=50)
    bench.add_argument("--chart", help="write a coverage-curve PNG (needs Pillow)")
    bench.set_defaults(func=_benchmark)

    replay = sub.add_parser("replay", help="run one mission and save an animated GIF")
    _add_map_args(replay)
    replay.add_argument("--out", help="output GIF path (needs Pillow)")
    replay.add_argument("--ascii", action="store_true", help="print the final map as text")
    replay.set_defaults(func=_replay)

    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    if args.command is None:
        _astar_demo()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
