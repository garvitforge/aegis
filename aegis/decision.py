"""Mission decision logic for AEGIS."""

from dataclasses import dataclass

from .autonomy import _shortest_known_path
from .distance import distance_map
from .exploration import frontier_cells
from .grid import Position
from .mapping import OccupancyMap


@dataclass(frozen=True)
class FrontierCandidate:
    frontier: Position
    vantage: Position
    path_length: int
    information_gain: int
    score: float


def _information_gain(known: OccupancyMap, frontier: Position) -> int:
    """Count unknown in-bounds cells directly adjacent to a frontier."""
    x, y = frontier
    return sum(
        1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if 0 <= nx < known.width
        and 0 <= ny < known.height
        and (nx, ny) not in known.known_free
        and (nx, ny) not in known.known_obstacles
    )


def _sort_key(candidate: FrontierCandidate) -> tuple:
    return (-candidate.score, candidate.path_length, candidate.frontier, candidate.vantage)


def frontier_candidates(known: OccupancyMap, start: Position) -> list[FrontierCandidate]:
    """Score reachable frontier approaches using one BFS distance map."""
    distances = distance_map(known, start)
    if not distances:
        return []

    candidates: list[FrontierCandidate] = []
    frontiers = frontier_cells(
        known.known_free, known.known_obstacles, known.width, known.height
    )
    for frontier in sorted(frontiers):
        x, y = frontier
        gain = _information_gain(known, frontier)
        for vantage in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            distance = distances.get(vantage)
            if distance is not None:
                candidates.append(
                    FrontierCandidate(frontier, vantage, distance, gain, 2.0 * gain - distance)
                )
    return sorted(candidates, key=_sort_key)


def frontier_candidates_reference(
    known: OccupancyMap, start: Position
) -> list[FrontierCandidate]:
    """Reference implementation using one A* search per candidate."""
    candidates: list[FrontierCandidate] = []
    frontiers = frontier_cells(
        known.known_free, known.known_obstacles, known.width, known.height
    )
    for frontier in sorted(frontiers):
        x, y = frontier
        gain = _information_gain(known, frontier)
        for vantage in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if vantage not in known.known_free:
                continue
            path = _shortest_known_path(known, start, vantage)
            if path is not None:
                distance = len(path) - 1
                candidates.append(
                    FrontierCandidate(frontier, vantage, distance, gain, 2.0 * gain - distance)
                )
    return sorted(candidates, key=_sort_key)


def best_frontier(known: OccupancyMap, start: Position) -> FrontierCandidate | None:
    """Return the highest-scoring reachable frontier candidate."""
    candidates = frontier_candidates(known, start)
    return candidates[0] if candidates else None


def nearest_frontier_candidate(
    known: OccupancyMap, start: Position
) -> FrontierCandidate | None:
    """Baseline strategy: choose the nearest reachable frontier approach."""
    candidates = frontier_candidates(known, start)
    return min(candidates, key=lambda c: (c.path_length, c.frontier, c.vantage)) if candidates else None
