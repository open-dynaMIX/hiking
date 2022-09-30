#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from hiking import commands
from hiking.arg_parsing import parse_arguments
from hiking.exceptions import HikingException, HikingJsonLoaderException
from hiking.import_export import JSON_IMPORT_EXAMPLE
from hiking.models import init_db
from hiking.utils import DATA_HOME


def main():
    args = parse_arguments(sys.argv[1:])

    DATA_HOME.mkdir(exist_ok=True)
    init_db()

    try:
        match args.command:
            case "show":
                commands.command_show(
                    args.ids,
                    args.daterange,
                    args.table_style,
                    args.order_key,
                    args.plot,
                )
            case "create" | "edit":
                commands.command_create_edit(pk=getattr(args, "id", None), gpx=args.gpx)
            case "delete":
                commands.command_delete(args.ids, args.all, args.force, args.quiet)
            case "import":
                commands.command_import(args.json_data)
            case "export":
                commands.command_export(args.export_dir, args.ids, args.daterange)

    except HikingJsonLoaderException as e:
        print(f"Invalid data in hiking.json: {e.args[0]}\n\nExpected format:\n")
        print(JSON_IMPORT_EXAMPLE)
    except HikingException as e:
        print(f"Error: {e}")


if __name__ == "__main__":  # pragma: no cover
    main()
