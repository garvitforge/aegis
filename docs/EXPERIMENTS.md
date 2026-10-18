# Experiments and benchmark methodology

AEGIS is a simulation prototype. This document records what the included benchmark measures and what it does not establish.

## Included scenarios

Run with:

```bash
aegis benchmark --output reports/benchmark.json
```

The command executes two fixed maps: `corridor` and `split_room`. It emits a JSON object with schema version, benchmark name, and one result per scenario.

## Metrics

- **Steps:** number of simulated cell moves.
- **Replans:** number of path-planning calls recorded by the mission.
- **Discoveries:** newly observed cells (free or obstacle) added to the partial map.
- **Coverage:** known free cells divided by the true number of traversable cells; the truth map is used only to score the simulation after the run, never by the planner.
- **Average planning time:** mean wall-clock time for recorded path-planning calls. It is hardware/runtime dependent and not expected to be bit-for-bit reproducible.
- **Safety stops:** count of mission stops triggered by the safety checks.
- **Final battery:** simulated battery remaining after the mission.

## Reproducibility

Map geometry and start positions are fixed. Algorithmic outputs should remain deterministic for a given Python implementation; measured timing is expected to vary. The automated benchmark test compares deterministic fields while validating timing values separately.

For a publishable comparison, record:
- Git commit SHA and Python version
- Scenario dimensions, obstacle layout, and start pose
- Strategy and configuration parameters
- Repeated timing samples and summary statistics
- Failure and incomplete-coverage cases, not only successful runs

## Current evidence

The bundled scenarios are smoke/regression benchmarks, not a statistically broad evaluation. They do not demonstrate superiority over other navigation systems or validate physical rescue performance. Claims about improvements should be supported by larger paired experiments on identical maps and multiple seeds.

## Next experiment

Generate a documented set of seeded maps, then compare nearest-frontier and information-gain strategies on each map. Report coverage, moves, return success, safety stops, and runtime distributions. Keep each strategy's access restricted to the same observations.
