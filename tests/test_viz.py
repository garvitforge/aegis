import os
import tempfile

import pytest

from aegis.experiment import run_experiment, run_frontier_strategy
from aegis.generators import random_map


def test_gif_and_chart_are_written() -> None:
    pytest.importorskip("PIL")
    from aegis.viz import save_coverage_chart, save_replay_gif

    truth, start = random_map(10, 10, 0.2, 0)
    result = run_frontier_strategy("scored", truth, start, 3, 300)
    report = run_experiment(maps=2, size=10, seed=0, curve_length=60)

    with tempfile.TemporaryDirectory() as tmp:
        gif = os.path.join(tmp, "replay.gif")
        png = os.path.join(tmp, "chart.png")
        frames = save_replay_gif(truth, start, list(result.positions), 3, gif)
        save_coverage_chart(report.curves, png)
        assert frames == result.moves + 1
        assert os.path.getsize(gif) > 0
        assert os.path.getsize(png) > 0
