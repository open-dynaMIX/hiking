import datetime
import itertools
import json
import tempfile
from pathlib import Path
from shutil import which

import pytest
from rich import box

from hiking import commands, interactivity
from hiking.db_utils import session
from hiking.exceptions import HikingException, HikingJsonLoaderException
from hiking.models import Hike
from hiking.tests.utils import ansi_escape
from hiking.utils import DEFAULT_BOX_STYLE, SlimDateRange

itertools.product()


@pytest.mark.parametrize(
    "do_edit, write_body",
    [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ],
)
@pytest.mark.parametrize(
    "set_gpx_interactively, set_gpx_as_arg",
    [(False, False), (True, False), (False, True), (True, True)],
)
@pytest.mark.parametrize("do_write", [True, False])
def test_command_create_edit(
    hike_factory,
    mocker,
    gpx_xml,
    gpx_file,
    do_edit,
    set_gpx_interactively,
    set_gpx_as_arg,
    write_body,
    do_write,
):
    def editor_call_mock(command: list):
        if not write_body:
            return
        with Path(command[1]).open("w") as f:
            f.write("# My awesome hike\nLorem ipsum\n")

    mocker.patch.object(commands.Confirm, "ask", return_value=do_write)
    mocker.patch.object(interactivity.FloatPrompt, "ask", return_value=23.5)
    mocker.patch.object(
        interactivity.IntPrompt,
        "ask",
        side_effect=[
            2310,  # elevation gain
            235,  # elevation loss
            304,  # duration in minutes
        ],
    )
    gpx_file_mock = mocker.patch.object(
        interactivity.Prompt,
        "ask",
        side_effect=[
            "not a date",  # expects a date; we test the loop
            "1970-01-01",  # give it what it wants
            "My awesome hike",  # set the hike title
            (
                str(gpx_file.absolute()) if set_gpx_interactively else None
            ),  # conditionally set gpx file
        ],
    )
    mocker.patch.object(interactivity, "call", new=editor_call_mock)

    hike = None
    kwargs = {}
    if do_edit:
        hike = hike_factory(body=None)
        kwargs["pk"] = hike.id
    if set_gpx_as_arg:
        kwargs["gpx"] = gpx_xml

    commands.command_create_edit(**kwargs)

    if not do_edit and not do_write:
        assert session.query(Hike).count() == 0
        return
    if do_edit and not do_write:
        assert session.query(Hike).count() == 1
        assert session.query(Hike).first() == hike
        return

    assert session.query(Hike).count() == 1

    db_hike = session.query(Hike).first()
    assert db_hike.date == datetime.date(1970, 1, 1)
    assert db_hike.name == hike.name if do_edit else db_hike.name
    if write_body:
        assert db_hike.body == "# My awesome hike\nLorem ipsum\n"
    else:
        assert db_hike.body is None
    assert db_hike.distance == 23.5
    assert db_hike.elevation_gain == 2310
    assert db_hike.elevation_loss == 235
    assert db_hike.duration == datetime.timedelta(minutes=304)

    # Only prompt for gpx file if none was provided as argument
    assert gpx_file_mock.call_count == (3 if set_gpx_as_arg else 4)


def test_command_create_edit_invalid_id():
    with pytest.raises(HikingException) as e:
        commands.command_create_edit(pk=23)
    assert e.value.args[0] == "No hike found with provided ID"


@pytest.mark.parametrize("delete_all", [True, False])
@pytest.mark.parametrize("force", [True, False])
@pytest.mark.parametrize("quiet", [True, False])
@pytest.mark.parametrize("do_write", [True, False])
def test_command_delete(
    snapshot, mocker, collection, capsys, delete_all, force, quiet, do_write
):
    hikes = collection.hikes.all()
    assert session.query(Hike).count() == 3

    if not force:
        mocker.patch.object(interactivity.Confirm, "ask", return_value=do_write)

    commands.command_delete(
        ids=[hikes[0].id, hikes[1].id], delete_all=delete_all, force=force, quiet=quiet
    )

    if not quiet:
        captured = capsys.readouterr()[0]
        assert ansi_escape(captured) == snapshot

    if force or do_write:
        if delete_all:
            assert session.query(Hike).count() == 0
            return
        assert session.query(Hike).count() == 1
        assert session.query(Hike).first() == hikes[2]
    elif not force and not do_write:
        assert session.query(Hike).count() == 3


def test_command_delete_failure(collection):
    hikes = collection.hikes.all()
    with pytest.raises(HikingException) as e:
        commands.command_delete(
            ids=[hikes[0].id, hikes[1].id, 23],
            delete_all=False,
            force=False,
            quiet=False,
        )
    assert e.value.args[0] == "Invalid ID(s) provided"

    with pytest.raises(HikingException) as e:
        commands.command_delete(
            ids=[23, 24], delete_all=False, force=False, quiet=False
        )
    assert e.value.args[0] == "No hikes found with provided ID(s)"


def test_command_import(snapshot, json_import_data):
    assert session.query(Hike).count() == 0
    commands.command_import(json_import_data)
    assert session.query(Hike).count() == 5

    for hike in session.query(Hike).all():
        assert hike.get_stats() == snapshot


@pytest.mark.parametrize("add_gpx", [False, True])
def test_command_import_update(snapshot, hike, gpx_file, add_gpx):
    assert session.query(Hike).count() == 1
    commands.command_import(
        [
            {
                "id": hike.id,
                "name": "abnegation hike",
                "date": "2022-02-26",
                "distance": 5.0,
                "elevation_gain": 298,
                "elevation_loss": 298,
                "duration": 75,
                "gpx_file": str(gpx_file.absolute()) if add_gpx else None,
            }
        ]
    )

    assert session.query(Hike).count() == 1
    assert session.query(Hike).first().get_stats() == snapshot
    assert session.query(Hike).first().gpx == snapshot


def test_command_import_failure(snapshot, hike):
    assert session.query(Hike).count() == 1
    valid_hike_data = {
        "id": hike.id,
        "name": "abnegation hike",
        "date": "2022-02-26",
        "distance": 5.0,
        "elevation_gain": 298,
        "elevation_loss": 298,
        "duration": 75,
        "gpx_file": None,
    }

    invalid_date = valid_hike_data.copy()
    invalid_date["date"] = "not a date"

    with pytest.raises(HikingJsonLoaderException) as e:
        commands.command_import([invalid_date])
    assert e.value.args[0] == "Wrong date format"

    invalid_duration = valid_hike_data.copy()
    invalid_duration["duration"] = "not a duration"

    with pytest.raises(HikingJsonLoaderException) as e:
        commands.command_import([invalid_duration])
    assert e.value.args[0] == "Wrong duration format"

    non_existent_gpx_file = valid_hike_data.copy()
    non_existent_gpx_file["gpx_file"] = "not/a/file"

    with pytest.raises(HikingJsonLoaderException) as e:
        commands.command_import([non_existent_gpx_file])
    assert e.value.args[0] == '*.gpx file "not/a/file" not found'

    with tempfile.NamedTemporaryFile(suffix=".gpx", mode="w+") as tf:
        tf.write("Not gpx xml")
        tf.flush()

        invalid_gpx_file = valid_hike_data.copy()
        invalid_gpx_file["gpx_file"] = tf.name

        with pytest.raises(HikingJsonLoaderException) as e:
            commands.command_import([invalid_gpx_file])
        assert e.value.args[0] == "Error parsing XML: syntax error: line 1, column 0"

    assert session.query(Hike).count() == 1


def test_command_import_from_export(hike, gpx_xml, export_dir):
    hike.gpx_xml = gpx_xml
    hike.save()

    export_dir = Path(export_dir)
    commands.command_export(
        export_dir=export_dir,
        ids=[hike.id],
        daterange=SlimDateRange(datetime.date.min, datetime.date.max),
        include_ids=False,
    )

    with (export_dir / "hikes.json").open("r") as f:
        data = json.loads(f.read())

    hike.delete()
    assert session.query(Hike).count() == 0

    commands.command_import(data)

    assert session.query(Hike).count() == 1

    db_hike = session.query(Hike).first()
    assert db_hike.gpx_xml == gpx_xml


def test_command_export_with_ids(snapshot, collection, export_dir):
    export_dir = Path(export_dir)
    commands.command_export(
        export_dir=export_dir,
        ids=[hike.id for hike in collection.hikes.all()],
        daterange=SlimDateRange(datetime.date.min, datetime.date.max),
        include_ids=True,
    )

    with (export_dir / "hikes.json").open("r") as f:
        data = json.loads(f.read())

    assert data == snapshot


@pytest.mark.parametrize(
    "has_gpx, open_external_viewer, has_gpx_viewer",
    [
        (False, False, False),
        (True, False, False),
        (True, True, False),
        (True, True, True),
        (True, False, True),
    ],
)
def test_command_show_detail(
    mocker,
    monkeypatch,
    capsys,
    snapshot,
    hike,
    gpx_xml,
    has_gpx,
    open_external_viewer,
    has_gpx_viewer,
):
    # Using `cat` here, just to be sure to get the path to some executable.
    # It will never be called, because of the mock one line below.
    monkeypatch.setattr(
        interactivity,
        "GPX_VIEWER",
        which("cat") if has_gpx_viewer else "not a path",
    )
    viewer_mock = mocker.patch.object(interactivity, "call")
    mocker.patch.object(interactivity.Confirm, "ask", return_value=open_external_viewer)
    if has_gpx:
        hike.gpx_xml = gpx_xml
        hike.save()

    commands.command_show(
        [hike.id],
        SlimDateRange(datetime.date.min, datetime.date.max),
        None,
        DEFAULT_BOX_STYLE,
        ("date", False),
        (),
    )

    if has_gpx and open_external_viewer and has_gpx_viewer:
        viewer_mock.assert_called_once()

    captured = capsys.readouterr()[0]

    assert ansi_escape(captured) == snapshot


@pytest.mark.parametrize(
    "order_param, reverse, daterange, search, table_style, plot_params",
    [
        (
            "date",
            False,
            SlimDateRange(datetime.date.min, datetime.date.max),
            None,
            DEFAULT_BOX_STYLE,
            (),
        ),
        (
            "date",
            True,
            SlimDateRange(datetime.date(2002, 6, 1), datetime.date(2012, 8, 1)),
            None,
            DEFAULT_BOX_STYLE,
            (),
        ),
        (
            "distance",
            True,
            SlimDateRange(datetime.date.min, datetime.date.max),
            None,
            box.DOUBLE,
            (),
        ),
        (
            "elevation_gain",
            False,
            SlimDateRange(datetime.date.min, datetime.date.max),
            None,
            box.DOUBLE,
            ("duration", "distance"),
        ),
        (
            "speed",
            True,
            SlimDateRange(datetime.date.min, datetime.date.max),
            None,
            DEFAULT_BOX_STYLE,
            ("date", "distance"),
        ),
        (
            "date",
            False,
            SlimDateRange(datetime.date.min, datetime.date.max),
            "Paul",
            DEFAULT_BOX_STYLE,
            (),
        ),
        (
            "date",
            False,
            SlimDateRange(datetime.date.min, datetime.date.max),
            "FOO",
            DEFAULT_BOX_STYLE,
            (),
        ),
    ],
)
def test_command_show_list(
    capsys,
    snapshot,
    collection,
    order_param,
    reverse,
    daterange,
    search,
    table_style,
    plot_params,
):
    hike = collection.hikes.first()
    hike.body = "foo"
    hike.save()
    commands.command_show(
        [],
        daterange,
        search,
        table_style,
        (order_param, reverse),
        plot_params,
    )

    captured = capsys.readouterr()[0]

    assert ansi_escape(captured) == snapshot


def test_command_show_no_hikes():
    with pytest.raises(HikingException) as e:
        commands.command_show(
            [],
            SlimDateRange(datetime.date.min, datetime.date.max),
            None,
            DEFAULT_BOX_STYLE,
            (),
            (),
        )

    assert e.value.args[0] == 'No hikes in DB. Add some hikes with "create" or "import"'


def test_command_show_no_hikes_with_params(hike):
    with pytest.raises(HikingException) as e:
        commands.command_show(
            [hike.id + 1],  # no hike with this ID
            SlimDateRange(datetime.date.min, datetime.date.max),
            None,
            DEFAULT_BOX_STYLE,
            (),
            (),
        )

    assert e.value.args[0] == "No hikes found with given parameters"
