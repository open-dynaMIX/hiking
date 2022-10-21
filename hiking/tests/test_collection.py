import pytest

from hiking.models import Hike


@pytest.mark.parametrize("field", [f.info for f in Hike.FIELDS])
def test_collection_attr_functions(collection, snapshot, field):
    assert collection.get_hikes_attr_list(field["name"]) == snapshot(
        name=f"{field['name']} - attr_list"
    )

    for calc in ["sum", "avg", "min", "max"]:
        if calc in field["supported_calculations"]:
            assert getattr(collection, calc)(field["name"]) == snapshot(
                name=f"{field['name']} - {calc} - raw"
            )
            assert collection.calc_and_format_value(calc, field["name"]) == snapshot(
                name=f"{field['name']} - {calc} - pretty"
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
def test_collection_hikes_stats(
    collection, snapshot, caplog, debug_logging, order_params
):
    stats = collection.get_hikes_stats(order_params)
    # remove the IDs for comparison
    for hike in stats:
        del hike[0]

    prefix = "-" if order_params[1] else ""
    assert stats == snapshot(name=f'order_param: "{prefix}{order_params[0]} - stats"')

    assert len(caplog.messages) == 3
    assert caplog.messages[0] == "BEGIN (implicit)"
    assert caplog.messages[2].startswith("[generated in 0.00")
    assert caplog.messages[1] == snapshot(
        name=f'order_param: "{prefix}{order_params[0]}" - query'
    )


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

    prefix = "-" if order_params[1] else ""

    assert stats == snapshot(name=f'order_param: "{prefix}{order_params[0]}" - stats')
    assert footer == snapshot(name=f'order_param: "{prefix}{order_params[0]}" - footer')
