import sys
from collections import namedtuple

import pytest

from hiking import __main__, commands
from hiking.__main__ import main
from hiking.tests.utils import ansi_escape

ArgsMock = namedtuple(
    "args",
    [
        "command",
        "id",
        "ids",
        "all",
        "force",
        "quiet",
        "json_data",
        "daterange",
        "table_style",
        "order_key",
        "plot",
        "gpx",
        "export_dir",
        "include_ids",
    ],
    defaults=(None,) * 13,
)


def test_main_end_to_end(snapshot, capsys, sys_argv, collection):
    sys.argv = ["tests", "show", "--order-key=-distance"]
    main()
    captured = capsys.readouterr()[0]
    assert ansi_escape(captured) == snapshot


@pytest.mark.parametrize(
    "command, args",
    [
        ("command_create_edit", ["create"]),
        ("command_delete", ["delete"]),
        ("command_import", ["import"]),
        ("command_export", ["export", "/tmp/"]),
    ],
)
def test_main_commands(mocker, sys_argv, command, args):
    mocker.patch.object(commands, command)
    mocked_args = ArgsMock(command=args[0])
    mocker.patch.object(
        __main__,
        "parse_arguments",
        return_value=mocked_args,
    )
    sys.argv = ["tests", *args]
    main()


def test_main_hiking_json_loader_exception(mocker, caplog, snapshot):
    args = ArgsMock(command="import", json_data=[{"foo": "bar"}])
    mocker.patch.object(
        __main__,
        "parse_arguments",
        return_value=args,
    )
    main()
    assert len(caplog.records) == 1
    assert caplog.records[0].msg == snapshot


def test_main_hiking_exception(mocker, caplog, snapshot):
    args = ArgsMock(command="delete", ids=[23])
    mocker.patch.object(
        __main__,
        "parse_arguments",
        return_value=args,
    )
    main()
    assert len(caplog.records) == 1
    assert caplog.records[0].msg == snapshot
