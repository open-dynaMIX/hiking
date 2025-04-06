import argparse
import datetime
import json
import os
from itertools import zip_longest
from pathlib import Path
from typing import Optional

import gpxpy
from rich import box

from hiking.import_export import JSON_IMPORT_EXAMPLE
from hiking.models import Hike
from hiking.utils import DATA_HOME, DEFAULT_BOX_STYLE, SlimDateRange

# TODO: find a way to auto-detect this from rich
BOX_FORMATS = [
    "ASCII",
    "ASCII2",
    "ASCII_DOUBLE_HEAD",
    "SQUARE",
    "SQUARE_DOUBLE_HEAD",
    "MINIMAL",
    "MINIMAL_HEAVY_HEAD",
    "MINIMAL_DOUBLE_HEAD",
    "SIMPLE",
    "SIMPLE_HEAD",
    "SIMPLE_HEAVY",
    "HORIZONTALS",
    "ROUNDED",
    "HEAVY",
    "HEAVY_EDGE",
    "HEAVY_HEAD",
    "DOUBLE",
    "DOUBLE_EDGE",
    "MARKDOWN",
]


def get_valid_fields_for_args(exclude: Optional[list] = None):
    exclude = exclude or []
    return [
        field.info["name"]
        for field in Hike.FIELDS
        if field.info["data_view"] and field.info["name"] not in exclude
    ]


class DateRangeType:
    description = (
        "Only include hikes contained in provided daterange (default: all hikes)"
    )
    examples = (
        "Valid examples:\n"
        "1970-01-01\n"
        "1970-01-01/1970-02-01\n"
        "1970-01-01/ (all hikes from start date)\n"
        "/1970-01-01 (all hikes until end date)"
    )
    help = f"{description}\n{examples}"

    def __call__(self, raw: str, *args, **kwargs):
        start = end = raw
        splitted = raw.split("/")
        if len(splitted) == 2 and all(splitted):
            start, end = splitted
        elif start.endswith("/"):
            start = start.rstrip("/")
            end = None
        elif end.startswith("/"):
            end = end.lstrip("/")
            start = None

        try:
            start = (
                datetime.datetime.strptime(start, "%Y-%m-%d").date()
                if start
                else datetime.date.min
            )
            end = (
                datetime.datetime.strptime(end, "%Y-%m-%d").date()
                if end
                else datetime.date.max
            )
        except ValueError as e:
            msg = f"{e.args[0]}\n{self.examples}"
            raise argparse.ArgumentTypeError(msg) from e
        return SlimDateRange(start, end)


class WritableDirPathType:
    def __call__(self, raw: str, *args, **kwargs):
        directory = Path(raw)
        if (
            not directory.exists()
            or not directory.is_dir()
            or not os.access(directory, os.W_OK)
        ):
            msg = (
                f'Cannot write to directory: "{directory.absolute()}". '
                f"Make sure it exists and is writable."
            )
            raise argparse.ArgumentTypeError(msg)
        return directory


class GPXFileType(argparse.FileType):
    def __call__(self, *args, **kwargs):
        file = super().__call__(*args, **kwargs)
        try:
            gpx_xml = file.read()
            gpxpy.parse(gpx_xml)
        except Exception as e:
            msg = f"Cannot read *.gpx file: {e!s}"
            raise argparse.ArgumentTypeError(msg) from e
        return gpx_xml


class JsonFileType(argparse.FileType):
    def __call__(self, *args, **kwargs):
        file = super().__call__(*args, **kwargs)
        try:
            data = json.load(file)
        except Exception as e:
            msg = f"Cannot read *.json file: {e!s}"
            raise argparse.ArgumentTypeError(msg) from e
        return data


def validate_order_key(value: str) -> tuple[str, bool]:
    reverse = False
    if value.startswith("-"):
        reverse = True
        value = value.lstrip("-")
    if value not in get_valid_fields_for_args():
        msg = "Invalid order_key"
        raise argparse.ArgumentTypeError(msg)
    return value, reverse


def validate_plot(value: str) -> tuple[str, str]:
    try:
        x, y = tuple(value.split(","))
        for i in x, y:
            assert i in get_valid_fields_for_args(["name"])
    except (ValueError, AssertionError) as e:
        msg = "plot"
        raise argparse.ArgumentTypeError(msg) from e
    else:
        return x, y


def validate_table_style(value: str) -> tuple[str, str]:
    try:
        box_style = getattr(box, value.upper())
    except AttributeError as e:
        msg = "Invalid table-style"
        raise argparse.ArgumentTypeError(msg) from e
    return box_style


def set_default_subparser(
    parser: argparse.ArgumentParser, default_subcommand: str, raw_args: list[str]
):
    subparser_found = False
    for arg in raw_args:
        if arg in ["-h", "--help"]:  # pragma: no cover
            break
    else:
        for x in parser._subparsers._actions:  # noqa: SLF001
            if not isinstance(x, argparse._SubParsersAction):  # noqa: SLF001
                continue
            for sp_name in x._name_parser_map:  # noqa: SLF001
                if sp_name in raw_args:
                    subparser_found = True
        if not subparser_found:
            raw_args.insert(0, default_subcommand)


def parse_arguments(raw_args: list[str]) -> argparse.Namespace:  # noqa: PLR0915
    """Parse all arguments."""

    def format_list(data: list[str]):
        data.sort()
        col_1 = data[: round(len(data) / 2)]
        col_2 = data[round(len(data) / 2) :]
        table_data = list(zip_longest(col_1, col_2, fillvalue=""))
        longest = 0
        for i in table_data:
            longest = max(longest, len(i[0]))
        result = [f"{i[0].ljust(longest)}{' ' * 5}{i[1]}" for i in table_data]
        return "\n".join(result)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter, prog="hiking"
    )

    debug_arg_dict = {
        "help": "Show debug information (log queries)",
        "action": "store_true",
    }

    subparsers = parser.add_subparsers(dest="command")

    show = subparsers.add_parser(
        "show",
        help="Show hike(s) (default)",
        description="Show hike(s) (default)",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    show.add_argument(
        "ids",
        metavar="ID",
        help="Hike ID",
        nargs="*",
        type=int,
    )

    show.add_argument(
        "-d",
        "--daterange",
        help=DateRangeType.help,
        type=DateRangeType(),
        default=SlimDateRange(datetime.date.min, datetime.date.max),
    )

    show.add_argument(
        "-s",
        "--search",
        help="Search for text in name and body (case insensitive)",
        type=str,
    )

    show.add_argument(
        "-t",
        "--table-style",
        help=(
            "Table format style (default: simple)\n"
            f"Available options:\n{format_list(BOX_FORMATS)}"
        ),
        default=DEFAULT_BOX_STYLE,
        type=validate_table_style,
    )

    show.add_argument(
        "-o",
        "--order-key",
        help=(
            'Key to use for hike sorting. To reverse, prepend with "-".\n'
            "Available options:\n"
            f"{format_list(get_valid_fields_for_args())}"
        ),
        default=("date", False),
        type=validate_order_key,
    )

    show.add_argument(
        "--plot",
        help=(
            "Fields to plot in a graph.\n"
            "*experimental*\n"
            "Example:\n"
            '"date,distance"\n'
            "Available options:\n"
            f"{format_list(get_valid_fields_for_args(exclude=['name']))}"
        ),
        default=(),
        type=validate_plot,
    )

    show.add_argument("--debug", **debug_arg_dict)

    create = subparsers.add_parser(
        "create",
        help="Create a new record",
        description="Create a new record.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    create.add_argument(
        "--gpx",
        metavar="GPX_FILE",
        type=GPXFileType("r"),
        help="Import from *.gpx-file",
    )

    create.add_argument("--debug", **debug_arg_dict)

    edit = subparsers.add_parser(
        "edit",
        help="Edit a record",
        description="Edit a record.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    edit.add_argument(
        "id",
        metavar="ID",
        help="Hike ID",
        type=int,
    )

    edit.add_argument(
        "--gpx",
        metavar="GPX_FILE",
        type=GPXFileType("r"),
        help="Import from *.gpx-file",
    )

    edit.add_argument("--debug", **debug_arg_dict)

    delete = subparsers.add_parser(
        "delete",
        help="Delete records by ID",
        description="Delete records by ID.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    delete.add_argument(
        "-f",
        "--force",
        help="Do not ask before deletion",
        action="store_true",
    )

    delete.add_argument(
        "-q",
        "--quiet",
        help="Do not display hikes before deletion",
        action="store_true",
    )

    delete.add_argument(
        "-a",
        "--all",
        help="Delete all hikes",
        action="store_true",
    )

    delete.add_argument(
        "ids",
        metavar="ID",
        help="Hike ID",
        nargs="*",
        type=int,
    )

    delete.add_argument("--debug", **debug_arg_dict)

    _import = subparsers.add_parser(
        "import",
        help="Import records from JSON",
        description=f"Import records from JSON.\nFormat:\n{JSON_IMPORT_EXAMPLE}",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    _import.add_argument(
        "json_data",
        metavar="JSON_FILE",
        help="Path to JSON file",
        type=JsonFileType("r"),
    )

    _import.add_argument("--debug", **debug_arg_dict)

    export = subparsers.add_parser(
        "export",
        help="Export records as JSON and GPX",
        description="Export records as JSON and GPX.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    export.add_argument(
        "export_dir",
        metavar="EXPORT_DIR",
        help="Path to export directory",
        type=WritableDirPathType(),
    )

    export.add_argument(
        "ids",
        metavar="ID",
        help="Hike ID",
        nargs="*",
        type=int,
    )

    export.add_argument(
        "-d",
        "--daterange",
        help=DateRangeType.help,
        type=DateRangeType(),
        default=SlimDateRange(datetime.date.min, datetime.date.max),
    )

    export.add_argument(
        "-i",
        "--include-ids",
        help='Include IDs in export. Needed for "update", must be omitted for "create"',
        action="store_true",
    )

    export.add_argument("--debug", **debug_arg_dict)

    set_default_subparser(parser, "show", raw_args)

    args = parser.parse_args(raw_args)

    if args.command == "delete" and not args.ids and not args.all:
        msg = "IDs or --all must be provided"
        raise parser.error(msg)
    if args.command == "delete" and args.ids and args.all:
        msg = "Ambiguous argument: IDs and --all provided"
        raise parser.error(msg)

    try:
        WritableDirPathType()(DATA_HOME.parent)
    except argparse.ArgumentTypeError as e:
        msg = f"Cannot write to user data director: {DATA_HOME.parent}"
        raise parser.error(msg) from e

    return args
