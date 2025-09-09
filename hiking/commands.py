from pathlib import Path
from typing import Optional

from rich import box
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.table import Table

from hiking.collection import HikeCollection
from hiking.db_utils import session
from hiking.exceptions import HikingException
from hiking.gpx import get_elevation_profile
from hiking.import_export import json_exporter, json_importer
from hiking.interactivity import display_gpx, user_create_edit_interaction
from hiking.models import Hike, get_filtered_query
from hiking.plot import plot
from hiking.utils import DEFAULT_BOX_STYLE, SlimDateRange, console


def get_table(
    collection: HikeCollection,
    order_params: tuple[str, bool],
    table_style: box.Box = box.SIMPLE,
    add_totals: bool = True,
) -> Table:
    data, footer = collection.get_collection_stats(order_params, add_totals=add_totals)
    headers = {field.info["name"]: field.info["pretty_name"] for field in Hike.FIELDS}

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
    table.add_column("GPX", justify="right", footer=footer and get_grid(footer[0]))
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
        xlabel=getattr(Hike, x_attr).info["pretty_name"],
        ylabel=getattr(Hike, y_attr).info["pretty_name"],
        x_limit_min=1 if x_attr != "date" else None,
    )


def command_create_edit(pk: Optional[int] = None, gpx: Optional[str] = None):
    """
    Create or edit a record.

    If `pk` is provided, `edit` will be performed.
    """
    hike = session.get(Hike, pk) if pk is not None else Hike()

    if not hike:
        msg = "No hike found with provided ID"
        raise HikingException(msg)

    if gpx:
        hike.load_gpx(gpx)

    user_create_edit_interaction(hike, is_import_from_gpx=bool(gpx))

    stats = hike.get_detail_stats()
    stats["GPX"] = "available" if hike.gpx_xml else "not available"

    if not pk:
        stats.pop("ID")

    print_detail_stats(stats)

    confirmation = Confirm.ask("Should this hike be written to the DB?")

    if not confirmation:  # pragma: no cover
        console.print("Aborting")
        return

    hike.save()


def command_delete(ids: list[int], delete_all: bool, force: bool, quiet: bool):
    collection = HikeCollection(
        hikes=get_filtered_query(ids=None if delete_all else ids, daterange=None)
    )

    if not collection.hikes.first():
        msg = "No hikes found with provided ID(s)"
        raise HikingException(msg)
    if ids and collection.hikes.count() < len(ids):
        msg = "Invalid ID(s) provided"
        raise HikingException(msg)

    if not quiet:
        console.print("This action will delete following hikes:\n")
        table = get_table(
            collection,
            ("date", False),
            add_totals=False,
        )
        console.print(table)

    if not force:
        confirmation = Confirm.ask("Are you sure you want them deleted?")

        if not confirmation:
            console.print("Aborting")
            return

    for hike in collection.hikes:
        hike.delete()


def command_import(json_data: list[dict]):
    json_importer(json_data)


def command_export(
    export_dir: Path, ids: list[int], daterange: "SlimDateRange", include_ids: bool
):
    query = get_filtered_query(ids=ids, daterange=daterange, load_all_columns=True)
    json_exporter(query, export_dir, include_ids)


def print_detail_stats(stats: dict, table_style: box = DEFAULT_BOX_STYLE):
    title = stats.pop("Name")
    table = Table(box=table_style, show_header=False, title=title, min_width=40)
    for k, v in stats.items():
        table.add_row(k, str(v))
    console.print(table)


def detail_view(hike: Hike, ask_gpx_viewer: bool):
    stats = hike.get_detail_stats()

    print_detail_stats(stats)
    console.print()

    md = Markdown(hike.body or "")
    if md:
        console.print(md)
        console.print()

    print(get_elevation_profile(hike))  # noqa: T201

    console.print()
    if ask_gpx_viewer:
        display_gpx(hike.gpx_xml)


def command_show(
    ids: list[int],
    daterange: "SlimDateRange",
    search: Optional[str],
    table_style: box,
    order_params: tuple[str, bool],
    no_gpx_viewer: bool,
    plot_params: tuple[Optional[str], Optional[str]],
) -> None:
    if not session.query(Hike).first():
        msg = 'No hikes in DB. Add some hikes with "create" or "import"'
        raise HikingException(msg)

    collection = HikeCollection(hikes=get_filtered_query(ids, daterange, search))
    if not collection.hikes.first():
        msg = "No hikes found with given parameters"
        raise HikingException(msg)

    if len(ids) != 1:
        table = get_table(collection, order_params, table_style)
        console.print(table)

    if len(ids) == 1:
        hike = collection.hikes.first()
        ask_gpx_viewer = hike.gpx_xml and not no_gpx_viewer
        detail_view(hike, ask_gpx_viewer)

    if plot_params:
        plot = draw_plot(collection, plot_params[0], plot_params[1])
        print(plot)  # noqa: T201
