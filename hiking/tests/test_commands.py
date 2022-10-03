import datetime
import itertools
from pathlib import Path

import pytest

from hiking import commands, interactivity
from hiking.exceptions import HikingException
from hiking.models import Hike, session

itertools.product()


@pytest.mark.parametrize(
    "do_edit, has_gpx, write_body",
    [
        (False, False, False),
        (False, False, True),
        (False, True, False),
        (False, True, True),
        (True, False, False),
        (True, False, True),
        (True, True, False),
        (True, True, True),
    ],
)
@pytest.mark.parametrize("do_write", [True, False])
def test_command_create_edit(
    hike_factory, mocker, gpx_xml, gpx_file, do_edit, has_gpx, write_body, do_write
):
    def editor_call_mock(command: list):
        if not write_body:
            return None
        with Path(command[1]).open("w") as f:
            f.write("# My awesome hike\nLorem ipsum\n")

    mocker.patch.object(interactivity.Confirm, "ask", return_value=do_write)
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
    mocker.patch.object(
        interactivity.Prompt,
        "ask",
        side_effect=[
            "not a date",  # expects a date; we test the loop
            "1970-01-01",  # give it what it wants
            "My awesome hike",  # set the hike title
            str(gpx_file.absolute()) if has_gpx else None,  # conditionally set gpx file
        ],
    )
    mocker.patch.object(interactivity, "call", new=editor_call_mock)

    hike = None
    kwargs = {}
    if do_edit:
        hike = hike_factory(body=None)
        kwargs["pk"] = hike.id
    if has_gpx:
        kwargs["gpx"] = gpx_xml

    commands.command_create_edit(**kwargs)

    if not do_edit and not do_write:
        assert session.query(Hike).count() == 0
        return
    elif do_edit and not do_write:
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


def test_command_create_edit_invalid_id():
    with pytest.raises(HikingException) as e:
        commands.command_create_edit(pk=23)
    assert e.value.args[0] == "No hike found with provided ID"


@pytest.mark.parametrize("all", [True, False])
@pytest.mark.parametrize("force", [True, False])
@pytest.mark.parametrize("quiet", [True, False])
@pytest.mark.parametrize("do_write", [True, False])
def test_command_delete(
    snapshot, mocker, collection, capsys, all, force, quiet, do_write
):
    hikes = collection.hikes.all()
    assert session.query(Hike).count() == 3

    if not force:
        mocker.patch.object(interactivity.Confirm, "ask", return_value=do_write)

    commands.command_delete(
        ids=[hikes[0].id, hikes[1].id], all=all, force=force, quiet=quiet
    )

    if not quiet:
        captured = capsys.readouterr()[0]
        assert captured == snapshot

    if force or do_write:
        if all:
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
            ids=[hikes[0].id, hikes[1].id, 23], all=False, force=False, quiet=False
        )
    assert e.value.args[0] == "Invalid ID(s) provided"

    with pytest.raises(HikingException) as e:
        commands.command_delete(ids=[23, 24], all=False, force=False, quiet=False)
    assert e.value.args[0] == "No hikes found with provided ID(s)"
