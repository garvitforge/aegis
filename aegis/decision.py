"""Mission decision logic for AEGIS."""

from dataclasses import dataclass

from .autonomy import _shortest_known_path
from .exploration import frontier_cells
from .mapping import OccupancyMap
from .grid import Position


@dataclass(frozen=True)
class FrontierCandidate:
    frontier: Position
    vantage: Position
    path_length: int
    information_gain: int
    score: float


def frontier_candidates(known: OccupancyMap, start: Position) -> list[FrontierCandidate]:
    """Build deterministic frontier candidates using distance and local information gain."""
    candidates: list[FrontierCandidate] = []
    frontiers = frontier_cells(
        known.known_free, known.known_obstacles, known.width, known.height
    )

    for frontier in sorted(frontiers):
        x, y = frontier
        for vantage in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if vantage not in known.known_free:
                continue
            path = _shortest_known_path(known, start, vantage)
            if path is None:
                continue
            information_gain = 0
            for nx, ny in (
                (frontier[0] + 1, frontier[1]),
                (frontier[0] - 1, frontier[1]),
                (frontier[0], frontier[1] + 1),
                (frontier[0], frontier[1] - 1),
            ):
                if 0 <= nx < known.width and 0 <= ny < known.height:
                    if (nx, ny) not in known.known_free and (nx, ny) not in known.known_obstacles:
                        information_gain += 1
            distance = len(path) - 1
            score = (2.0 * information_gain) - distance
            candidates.append(
                FrontierCandidate(frontier, vantage, distance, information_gain, score)
            )

    return sorted(
        candidates,
        key=lambda c: (-c.score, c.path_length, c.frontier, c.vantage),
    )


def best_frontier(known: OccupancyMap, start: Position) -> FrontierCandidate | None:
    """Return the highest-scoring reachable frontier candidate."""
    candidates = frontier_candidates(known, start)
    return candidates[0] if candidates else None
