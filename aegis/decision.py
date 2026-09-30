"""Mission decision logic for AEGIS."""

from dataclasses import dataclass

from .autonomy import _shortest_known_path
from .distance import distance_map
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


def _information_gain(known: OccupancyMap, frontier: Position) -> int:
    """Count still-unknown in-bounds cells directly adjacent to a frontier cell."""
    x, y = frontier
    gain = 0
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nx < known.width and 0 <= ny < known.height:
            if (nx, ny) not in known.known_free and (nx, ny) not in known.known_obstacles:
                gain += 1
    return gain


def _sort_key(c: FrontierCandidate) -> tuple:
    return (-c.score, c.path_length, c.frontier, c.vantage)


def frontier_candidates(known: OccupancyMap, start: Position) -> list[FrontierCandidate]:
    """Build deterministic frontier candidates using distance and local information gain.

    Uses one breadth-first distance map from ``start`` instead of one A* search
    per candidate. Results are identical to ``frontier_candidates_reference``
    (checked by differential tests), but much cheaper to compute.
    """
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
            if distance is None:
                continue
            candidates.append(
                FrontierCandidate(frontier, vantage, distance, gain, (2.0 * gain) - distance)
            )

    return sorted(candidates, key=_sort_key)


def frontier_candidates_reference(known: OccupancyMap, start: Position) -> list[FrontierCandidate]:
    """Slow reference implementation: one A* search per candidate.

    Kept on purpose as a correctness oracle for ``frontier_candidates``.
    """
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
            gain = _information_gain(known, frontier)
            distance = len(path) - 1
            candidates.append(
                FrontierCandidate(frontier, vantage, distance, gain, (2.0 * gain) - distance)
            )

    return sorted(candidates, key=_sort_key)


def best_frontier(known: OccupancyMap, start: Position) -> FrontierCandidate | None:
    """Return the highest-scoring reachable frontier candidate."""
    candidates = frontier_candidates(known, start)
    return candidates[0] if candidates else None


def nearest_frontier_candidate(known: OccupancyMap, start: Position) -> FrontierCandidate | None:
    """Baseline strategy: go to the closest frontier, ignoring information gain."""
    candidates = frontier_candidates(known, start)
    if not candidates:
        return None
    return min(candidates, key=lambda c: (c.path_length, c.frontier, c.vantage))
