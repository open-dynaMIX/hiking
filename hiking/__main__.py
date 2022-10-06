#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sys

from hiking import commands
from hiking.arg_parsing import parse_arguments
from hiking.exceptions import HikingException, HikingJsonLoaderException
from hiking.import_export import JSON_IMPORT_EXAMPLE
from hiking.models import create_tables
from hiking.utils import DATA_HOME

logger = logging.getLogger(__name__)


def main():
    args = parse_arguments(sys.argv[1:])

    DATA_HOME.mkdir(exist_ok=True)
    create_tables()

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
                commands.command_export(
                    args.export_dir, args.ids, args.daterange, args.include_ids
                )

    except HikingJsonLoaderException as e:
        logger.warning(
            f"Invalid data in hiking.json: {e.args[0]}\n\nExpected format:\n{JSON_IMPORT_EXAMPLE}"
        )
    except HikingException as e:
        logger.error(f"Error: {e}")
    except (KeyboardInterrupt, EOFError):  # pragma: no cover
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
