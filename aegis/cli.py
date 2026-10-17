"""Command-line interface for AEGIS demos and reproducible benchmarks."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .benchmark import run_default_benchmark
from .grid import GridMap
from .planning import astar


def _demo() -> int:
    grid = GridMap(
        width=12,
        height=8,
        obstacles=frozenset({
            (3, 0), (3, 1), (3, 2),
            (6, 3), (7, 3), (8, 3),
            (9, 5), (9, 6),
        }),
    )
    start, goal = (0, 0), (11, 7)
    path = astar(grid, start, goal)
    print(f"AEGIS A* demo: {start} -> {goal}")
    if not path:
        print("No path found.")
        return 1
    print(f"Path length: {len(path) - 1} moves")
    print(" -> ".join(map(str, path)))
    return 0


def _benchmark(output: str | None) -> int:
    results = [asdict(result) for result in run_default_benchmark()]
    payload = {
        "schema_version": 1,
        "project": "AEGIS",
        "benchmark": "default_scenarios",
        "results": results,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if output:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {len(results)} benchmark results to {destination}")
    else:
        print(rendered)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aegis",
        description="Simulation-first autonomous exploration and planning tools.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("demo", help="run the A* path-planning demo")
    benchmark_parser = subparsers.add_parser(
        "benchmark", help="run deterministic benchmark scenarios"
    )
    benchmark_parser.add_argument(
        "--output", "-o", help="write JSON results to this path instead of stdout"
    )
    args = parser.parse_args()
    if args.command == "benchmark":
        raise SystemExit(_benchmark(args.output))
    raise SystemExit(_demo())


if __name__ == "__main__":
    main()
