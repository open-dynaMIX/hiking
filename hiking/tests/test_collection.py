import pytest

from hiking.models import Hike


@pytest.mark.parametrize("field", [f.info for f in Hike.FIELDS])
def test_collection_attr_functions(collection, snapshot, field):
    assert collection.get_hikes_attr_list(field["name"]) == snapshot(
        name=f"{field['name']} - attr_list"
    )

    if "sum" in field["supported_calculations"]:
        assert collection.sum(field["name"]) == snapshot(
            name=f"{field['name']} - sum - raw"
        )
        assert collection.calc_and_format_value("sum", field["name"]) == snapshot(
            name=f"{field['name']} - sum - pretty"
        )

    if "avg" in field["supported_calculations"]:
        assert collection.avg(field["name"]) == snapshot(
            name=f"{field['name']} - avg - raw"
        )
        assert collection.calc_and_format_value("avg", field["name"]) == snapshot(
            name=f"{field['name']} - avg - pretty"
        )

    if "max" in field["supported_calculations"]:
        assert collection.max(field["name"]) == snapshot(
            name=f"{field['name']} - max - raw"
        )
        assert collection.calc_and_format_value("max", field["name"]) == snapshot(
            name=f"{field['name']} - max - pretty"
        )

    if "min" in field["supported_calculations"]:
        assert collection.min(field["name"]) == snapshot(
            name=f"{field['name']} - min - raw"
        )
        assert collection.calc_and_format_value("min", field["name"]) == snapshot(
            name=f"{field['name']} - min - pretty"
        )


@pytest.mark.parametrize(
    "order_params",
    [
        ("date", False),
        ("date", True),
        ("elevation_gain", False),
        ("elevation_gain", True),
    ],
)
def test_collection_hikes_stats(collection, snapshot, order_params):
    stats = collection.get_hikes_stats(order_params)
    # remove the IDs for comparison
    for hike in stats:
        del hike[0]

    assert stats == snapshot


def test_collection_get_totals(collection, snapshot):
    assert collection.get_totals() == snapshot


@pytest.mark.parametrize(
    "order_params",
    [
        ("date", False),
        ("date", True),
        ("elevation_gain", False),
        ("elevation_gain", True),
    ],
)
def test_collection_collection_stats(collection, snapshot, order_params):
    stats, footer = collection.get_collection_stats(order_params)
    # remove the IDs for comparison
    for hike in stats:
        del hike[0]

    assert stats == snapshot
    assert footer == snapshot
