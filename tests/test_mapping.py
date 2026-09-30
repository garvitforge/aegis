from aegis.mapping import OccupancyMap


def test_map_update_records_new_knowledge() -> None:
    known = OccupancyMap(
        width=5,
        height=5,
        known_free={(2, 2)},
        known_obstacles=set(),
    )

    known.update({(2, 3)}, {(2, 4)})

    assert (2, 3) in known.known_free
    assert (2, 4) in known.known_obstacles


def test_map_rejects_overlapping_cells() -> None:
    try:
        OccupancyMap(
            width=3,
            height=3,
            known_free={(1, 1)},
            known_obstacles={(1, 1)},
        )
    except ValueError:
        return

    raise AssertionError("Expected overlapping map cells to be rejected.")
