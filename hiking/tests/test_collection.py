import pytest

from hiking.models import Hike


@pytest.mark.parametrize("attr, config", [(a, c) for a, c in Hike.FIELD_PROPS.items()])
def test_collection_attr_functions(collection, snapshot, attr, config):
    assert collection.get_hikes_attr_list(attr) == snapshot

    if "sum" in config["supported_calculations"]:
        assert collection.sum(attr) == snapshot
        assert collection.calc_and_format_value("sum", attr) == snapshot

    if "avg" in config["supported_calculations"]:
        assert collection.avg(attr) == snapshot
        assert collection.calc_and_format_value("avg", attr) == snapshot

    if "max" in config["supported_calculations"]:
        assert collection.max(attr) == snapshot
        assert collection.calc_and_format_value("max", attr) == snapshot

    if "min" in config["supported_calculations"]:
        assert collection.min(attr) == snapshot
        assert collection.calc_and_format_value("min", attr) == snapshot


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
