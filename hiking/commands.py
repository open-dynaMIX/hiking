from pathlib import Path
from typing import List, Tuple

from rich import box
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.table import Table

from hiking.collection import HikeCollection
from hiking.db_utils import get_collection, get_filtered_query
from hiking.exceptions import HikingException
from hiking.gpx import get_elevation_profile
from hiking.import_export import json_exporter, json_importer
from hiking.interactivity import display_gpx, user_create_edit_interaction
from hiking.models import Hike, session
from hiking.plot import plot
from hiking.utils import DEFAULT_BOX_STYLE, SlimDateRange, console


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


def command_create_edit(pk: int = None, gpx: str = None):
    """
    Create or edit a record.

    If `pk` is provided, `edit` will be performed.
    """
    hike = session.query(Hike).get(pk) if pk else Hike()

    if not hike:
        console.print("No hike found with provided ID")
        return

    if gpx:
        hike.load_gpx(gpx)

    user_create_edit_interaction(hike)

    stats = hike.get_detail_stats()
    stats["GPX"] = "available" if hike.gpx_xml else "not available"

    if not pk:
        stats.pop("ID")

    print_detail_stats(stats)

    confirmation = Confirm.ask("Should this hike be written to the DB?")

    if not confirmation:
        print("Aborting")
        return

    hike.save()


def command_delete(ids: List[int], all: bool, force: bool, quiet: bool):
    query = session.query(Hike)
    if not all:
        query = session.query(Hike).filter(Hike.id.in_(ids))
    if not query.first():
        console.print("No hikes found with provided ID(s)")
        return
    elif query.count() < len(ids):
        raise HikingException("Invalid ID(s) provided")

    if not quiet:
        console.print("This action will delete following hikes:\n")
        table = get_table(
            HikeCollection(hikes=query, session=session),
            ("date", False),
            add_totals=False,
        )
        console.print(table)

    if not force:
        confirmation = Confirm.ask("Are you sure you want them deleted?")

        if not confirmation:
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
        console.print('No hikes in DB. Add some hikes with "create" or "import"')
        return

    collection = get_collection(ids, daterange)
    if not collection.hikes.first():
        console.print("No hikes found")
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

        console.print()
        display_gpx(hike.gpx_xml)

    if plot_params:
        plot_params = draw_plot(collection, plot_params[0], plot_params[1])
        console.print(plot_params)
