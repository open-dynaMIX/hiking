#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import List, Tuple

import gpxpy
from rich import box
from rich.markdown import Markdown
from rich.table import Table

from hiking.arg_parsing import parse_arguments
from hiking.db_utils import get_collection, get_filtered_query
from hiking.exceptions import HikingException, HikingJsonLoaderException
from hiking.gpx import get_elevation_profile
from hiking.hike import HikeCollection
from hiking.import_export import JSON_IMPORT_EXAMPLE, json_exporter, json_importer
from hiking.interactivity import user_create_edit_interaction
from hiking.models import Hike, init_db, session
from hiking.plot import plot
from hiking.utils import DATA_HOME, DEFAULT_BOX_STYLE, SlimDateRange, console


def get_table(
    collection: HikeCollection,
    order_params: Tuple[str, bool],
    table_style: box.Box = box.SIMPLE,
    add_totals: bool = True,
) -> Table:
    data, footer = collection.get_collection_stats(order_params, add_totals=add_totals)
    headers = {attr: config["pretty_name"] for attr, config in Hike.FIELD_PROPS.items()}

    arrow = "▲" if order_params[1] else "▼"
    headers[order_params[0]] = f"{headers[order_params[0]]} {arrow}"

    table = Table(
        title="Hikes",
        show_header=True,
        show_footer=bool(footer),
        header_style="bold",
        box=table_style,
    )

    def get_grid(content: dict):
        if isinstance(content, str):
            return content

        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column(justify="right")
        for k, v in content.items():
            grid.add_row(k, v)
        return grid

    table.add_column("ID", justify="right", footer=footer and get_grid(footer[0]))
    table.add_column("Date", justify="left", footer=footer and get_grid(footer[1]))
    table.add_column("Name", justify="left", footer=footer and get_grid(footer[2]))
    table.add_column("➡ km", justify="right", footer=footer and get_grid(footer[3]))
    table.add_column("⬈ m", justify="right", footer=footer and get_grid(footer[4]))
    table.add_column("⬊ m", justify="right", footer=footer and get_grid(footer[5]))
    table.add_column("⏱", justify="right", footer=footer and get_grid(footer[6]))
    table.add_column("km/h", justify="right", footer=footer and get_grid(footer[7]))

    for d in data:
        table.add_row(*d)

    return table


def draw_plot(
    collection: HikeCollection, x_attr: str = "date", y_attr: str = "distance"
):
    x = collection.get_hikes_attr_list(x_attr)
    y = collection.get_hikes_attr_list(y_attr)
    return plot(
        x=x,
        y=y,
        xlabel=Hike.FIELD_PROPS[x_attr]["pretty_name"],
        ylabel=Hike.FIELD_PROPS[y_attr]["pretty_name"],
        x_limit_min=1,
    )


def create_edit_stats_and_write(stats: dict, hike: Hike):
    print_detail_stats(stats)

    try:
        confirmation = input("Should this hike be written to the DB? Y/n: ")
    except (KeyboardInterrupt, EOFError):
        return

    if confirmation.lower() not in ["y", "j"]:
        print("Aborting")
        return

    hike.save()


def command_edit(_id: int):
    hike = session.query(Hike).get(_id)

    if not hike:
        print("No hike found with provided ID")
        return

    user_create_edit_interaction(hike)

    stats = hike.get_detail_stats()
    stats["GPX"] = "available" if hike.gpx_xml else "not available"

    create_edit_stats_and_write(stats, hike)


def command_create(gpx=None):
    hike = Hike()

    if gpx:
        gpx_obj = gpxpy.parse(gpx)
        hike.date = gpx_obj.time.date() if gpx_obj.time else None
        hike.name = gpx_obj.name
        hike.distance = round(gpx_obj.length_3d() / 1000, 2)
        hike.elevation_gain = round(gpx_obj.get_uphill_downhill().uphill)
        hike.elevation_loss = round(gpx_obj.get_uphill_downhill().downhill)
        hike.duration = gpx_obj.get_duration()
        hike.duration = gpx_obj.get_duration()
        hike.gpx_xml = gpx

    user_create_edit_interaction(hike)

    stats = hike.get_detail_stats()
    stats["gpx"] = "available" if hike.gpx_xml else "not available"
    stats.pop("ID")

    create_edit_stats_and_write(stats, hike)


def command_delete(ids: List[int], all: bool, force: bool, quiet: bool):
    query = session.query(Hike)
    if not all:
        query = session.query(Hike).filter(Hike.id.in_(ids))
    if not query.first():
        print("No hikes found with provided IDs")
        return
    elif query.count() < len(ids):
        raise HikingException("Invalid ID(s) provided")

    if not quiet:
        print("This action will delete following hikes:\n")
        table = get_table(
            HikeCollection(hikes=query, session=session),
            ("date", False),
            add_totals=False,
        )
        console.print(table)

    if not force:
        try:
            confirmation = input("\nAre you sure you want them deleted? Y/n: ")
        except (KeyboardInterrupt, EOFError):
            return

        if confirmation.lower() not in ["y", "j"]:
            print("Aborting")
            return

    for hike in query:
        hike.delete()


def command_import(json_data: dict):
    json_importer(json_data)


def command_export(export_dir: Path, ids: List[int], daterange: "SlimDateRange"):
    query = get_filtered_query(ids, daterange)
    json_exporter(query, export_dir)


def print_detail_stats(stats: dict, table_style: box = DEFAULT_BOX_STYLE):
    title = stats.pop("Name")
    table = Table(box=table_style, show_header=False, title=title, min_width=40)
    for k, v in stats.items():
        table.add_row(k, str(v))
    console.print(table)


def command_show(
    ids: List[int],
    daterange: "SlimDateRange",
    table_style: box,
    order_params: Tuple[str, bool],
    plot_params: Tuple[str, str],
) -> None:
    if not session.query(Hike).first():
        print('No hikes in DB. Add some hikes with "create" or "import"')
        return

    collection = get_collection(ids, daterange)
    if not collection.hikes.first():
        print("No hikes found")
        return

    if len(ids) != 1:
        table = get_table(collection, order_params, table_style)
        console.print(table)

    if len(ids) == 1:
        hike = collection.hikes.first()
        stats = hike.get_detail_stats()

        print_detail_stats(stats, table_style)
        console.print()

        md = Markdown(hike.body or "")
        if md:
            console.print(md)
            console.print()

        print(get_elevation_profile(hike))

    if plot_params:
        plot_params = draw_plot(collection, plot_params[0], plot_params[1])
        print(plot_params)


def main():
    args = parse_arguments(sys.argv[1:])

    DATA_HOME.mkdir(exist_ok=True)
    init_db()

    try:
        match args.command:
            case "show":
                command_show(
                    args.ids,
                    args.daterange,
                    args.table_style,
                    args.order_key,
                    args.plot,
                )
            case "create":
                command_create(args.gpx)
            case "delete":
                command_delete(args.ids, args.all, args.force, args.quiet)
            case "edit":
                command_edit(args.id)
            case "import":
                command_import(args.json_data)
            case "export":
                command_export(args.export_dir, args.ids, args.daterange)

    except HikingJsonLoaderException as e:
        print(f"Invalid data in hiking.json: {e.args[0]}\n\nExpected format:\n")
        print(JSON_IMPORT_EXAMPLE)
    except HikingException as e:
        print(f"Error: {e}")


if __name__ == "__main__":  # pragma: no cover
    main()
