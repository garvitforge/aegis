# Exploration Strategy

AEGIS does not always know the complete environment.

A real robot receives observations incrementally, so the simulator needs to distinguish:

- **Known free space**
- **Known obstacles**
- **Unknown space**
- **Frontier cells** — unknown cells adjacent to known free space

The current exploration primitive identifies frontier cells and selects the nearest reachable frontier.

## Why frontiers?

Instead of blindly wandering, a robot can deliberately move toward the boundary between what it knows and what it does not know.

The current implementation is intentionally simple. Future versions can score frontiers using:

- Travel distance
- Expected information gain
- Obstacle risk
- Battery reserve
- Previously visited areas
- Mission priorities

The scoring model should remain measurable and testable.
