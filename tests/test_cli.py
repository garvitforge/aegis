import json

from aegis.cli import _benchmark


def test_benchmark_cli_writes_valid_json(tmp_path) -> None:
    destination = tmp_path / "reports" / "benchmark.json"

    assert _benchmark(str(destination)) == 0

    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["project"] == "AEGIS"
    assert {item["name"] for item in payload["results"]} == {
        "corridor",
        "split_room",
    }
    assert all(item["coverage"] > 0 for item in payload["results"])
