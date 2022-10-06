import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from rich import box

from hiking import arg_parsing
from hiking.arg_parsing import parse_arguments
from hiking.utils import SlimDateRange


@pytest.mark.parametrize(
    "value, expected, success",
    [
        (
            "1970-01-01/1970-02-01",
            SlimDateRange(datetime.date(1970, 1, 1), datetime.date(1970, 2, 1)),
            True,
        ),
        (
            "1970-01-01/",
            SlimDateRange(datetime.date(1970, 1, 1), datetime.date.max),
            True,
        ),
        (
            "/1970-02-01",
            SlimDateRange(datetime.date.min, datetime.date(1970, 2, 1)),
            True,
        ),
        (
            "1970-01-01",
            SlimDateRange(datetime.date(1970, 1, 1), datetime.date(1970, 1, 1)),
            True,
        ),
        (
            "invalid",
            None,
            False,
        ),
    ],
)
def test_date_range_type(value, expected, success):
    if not success:
        with pytest.raises(SystemExit):
            parse_arguments(["show", "--daterange", value])
        return

    args = parse_arguments(["show", "--daterange", value])
    assert args.daterange == expected


def test_writable_dir_path_type_failure():
    with pytest.raises(SystemExit):
        parse_arguments(["export", f"/{uuid4()}"])


@pytest.mark.parametrize("success", [True, False])
def test_gpx_file_type(gpx_file, gpx_xml, json_file, success):
    if not success:
        with pytest.raises(SystemExit):
            parse_arguments(["create", "--gpx", str(json_file.absolute())])
        return

    args = parse_arguments(["create", "--gpx", str(gpx_file.absolute())])
    assert args.gpx == gpx_xml


@pytest.mark.parametrize("success", [True, False])
def test_json_file_type(gpx_file, json_file, json_import_data, success):
    if not success:
        with pytest.raises(SystemExit):
            parse_arguments(["import", str(gpx_file.absolute())])
        return

    args = parse_arguments(["import", str(json_file.absolute())])
    assert args.json_data == json_import_data


@pytest.mark.parametrize(
    "value, success",
    [
        ("date", True),
        ("elevation_loss", True),
        ("distance", True),
        ("id", True),
        ("duration", True),
        ("name", True),
        ("elevation_gain", True),
        ("speed", True),
        ("invalid", False),
    ],
)
@pytest.mark.parametrize("reverse", [False, True])
def test_validate_order_key(value, success, reverse):
    arg_prefix = "-" if reverse else ""
    arg = f"--order-key={arg_prefix}{value}"
    if not success:
        with pytest.raises(SystemExit):
            parse_arguments(["show", arg])
        return

    args = parse_arguments(["show", arg])
    assert args.order_key == (value, reverse)


@pytest.mark.parametrize(
    "value1, value2, success",
    [
        ("date", "elevation_loss", True),
        ("elevation_loss", "distance", True),
        ("distance", "id", True),
        ("id", "elevation_gain", True),
        ("elevation_gain", "speed", True),
        ("speed", "duration", True),
        ("duration", "invalid", False),
        ("name", "duration", False),
    ],
)
def test_validate_plot(value1, value2, success):
    if not success:
        with pytest.raises(SystemExit):
            parse_arguments(["show", "--plot", f"{value1},{value2}"])
        return

    args = parse_arguments(["show", "--plot", f"{value1},{value2}"])
    assert args.plot == (value1, value2)


@pytest.mark.parametrize(
    "value, expected, success",
    [
        ("HEAVY_EDGE", box.HEAVY_EDGE, True),
        ("SIMPLE", box.SIMPLE, True),
        ("simple", box.SIMPLE, True),
        ("INVALID", None, False),
    ],
)
def test_validate_box_style(value, expected, success):
    if not success:
        with pytest.raises(SystemExit):
            parse_arguments(["show", f"--table-style={value}"])
        return

    args = parse_arguments(["show", f"--table-style={value}"])
    assert args.table_style == expected


def test_set_default_subparser():
    args = parse_arguments(["--table-style=SIMPLE"])
    assert args.table_style == box.SIMPLE


def test_delete_ids_and_all():
    with pytest.raises(SystemExit):
        parse_arguments(["delete", "--all", "1", "2", "3"])
    with pytest.raises(SystemExit):
        parse_arguments(["delete"])


def test_data_home_not_writable(monkeypatch):
    monkeypatch.setattr(arg_parsing, "DATA_HOME", Path(f"/{uuid4()}"))

    with pytest.raises(SystemExit):
        parse_arguments([])
