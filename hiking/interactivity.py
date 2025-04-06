import datetime
import tempfile
from pathlib import Path
from shutil import which
from subprocess import call
from typing import Optional, Union

import gpxpy
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from hiking.models import Hike
from hiking.utils import EDITOR, GPX_VIEWER, console


def call_external_command(
    command: str, initial_content: Optional[str] = None, return_content: bool = False
):
    with tempfile.NamedTemporaryFile(
        suffix=".gpx", mode="w+" if return_content else "w"
    ) as tf:
        if initial_content:
            tf.write(initial_content)
            tf.flush()
        call([command, tf.name])  # noqa: S603

        if return_content:
            tf.seek(0)
            return tf.read()


def display_gpx(gpx_xml: str):
    if not which(GPX_VIEWER):
        console.print("GPXSee not found. Install it to view your gpx")
        return

    confirmation = Confirm.ask("Open external GPX-viewer?")

    if not confirmation:
        console.print("Aborting")
        return
    call_external_command("/usr/bin/gpxsee", initial_content=gpx_xml)


def editor_input(initial_text: Union[str, None] = None):
    edited_text = call_external_command(
        EDITOR, initial_content=initial_text, return_content=True
    )

    edit_strip_changes = (
        edited_text.replace(initial_text, "") if initial_text else edited_text
    )
    if not edit_strip_changes or edit_strip_changes.isspace():
        return None
    return edited_text


def single_interaction(attr: str, attr_config: dict, hike: Hike):
    prompt = attr_config["prompt"]
    default = attr_config["default"]
    prompt_class = attr_config["prompt_class"]
    assignment_func = attr_config["assignment_func"]
    use_editor = attr_config["use_editor"]
    exceptions = attr_config["exceptions"]
    required = attr_config["required"]
    show_default = default is not None

    while True:
        if not use_editor:
            user_input = prompt_class.ask(
                prompt, default=default, show_default=show_default
            )
        else:
            user_input = editor_input(default)

        if user_input:
            if exceptions:
                try:
                    setattr(hike, attr, assignment_func(user_input))
                except exceptions as e:
                    console.print(e)
                    continue
                break
            setattr(hike, attr, assignment_func(user_input))
            break
        if not user_input and (getattr(hike, attr) or not required):
            break


def user_create_edit_interaction(hike: Hike, is_import_from_gpx: bool):
    def validate_gpx(raw_path: str):
        path = Path(raw_path)
        error_msg = "Cannot read *.gpx file"
        assert path.is_file(), error_msg
        assert path.exists(), error_msg
        with path.open("r") as f:
            xml_data = f.read()
        assert gpxpy.parse(xml_data), error_msg
        return xml_data

    attr_map = {
        "date": {
            "prompt": "Date of hike (YYYY-MM-DD)",
            "default": str(hike.date) if hike.date else None,
            "prompt_class": Prompt,
            "exceptions": (ValueError,),
            "assignment_func": lambda v: datetime.datetime.strptime(
                v, "%Y-%m-%d"
            ).date(),
            "required": True,
            "use_editor": False,
        },
        "name": {
            "prompt": "Name of hike",
            "default": hike.name,
            "prompt_class": Prompt,
            "exceptions": (),
            "assignment_func": lambda v: v,
            "required": True,
            "use_editor": False,
        },
        "body": {
            "prompt": None,
            "default": hike.body,
            "prompt_class": None,
            "exceptions": (),
            "assignment_func": lambda v: v,
            "required": False,
            "use_editor": True,
        },
        "distance": {
            "prompt": "Distance of hike in km",
            "default": hike.distance,
            "prompt_class": FloatPrompt,
            "exceptions": (ValueError,),
            "assignment_func": lambda v: float(v),
            "required": True,
            "use_editor": False,
        },
        "elevation_gain": {
            "prompt": "Elevation gain of hike in m",
            "default": hike.elevation_gain,
            "prompt_class": IntPrompt,
            "exceptions": (ValueError,),
            "assignment_func": lambda v: int(v),
            "required": True,
            "use_editor": False,
        },
        "elevation_loss": {
            "prompt": "Elevation loss of hike in m",
            "default": hike.elevation_loss,
            "prompt_class": IntPrompt,
            "exceptions": (ValueError,),
            "assignment_func": lambda v: int(v),
            "required": True,
            "use_editor": False,
        },
        "duration": {
            "prompt": "Duration of hike in minutes",
            "default": (
                round(hike.duration.total_seconds() / 60) if hike.duration else None
            ),
            "prompt_class": IntPrompt,
            "exceptions": (ValueError,),
            "assignment_func": lambda v: datetime.timedelta(minutes=float(v)),
            "required": True,
            "use_editor": False,
        },
        "gpx_xml": {
            "prompt": "Path to *.gpx file (optional)",
            "default": None,
            "prompt_class": Prompt,
            "exceptions": (Exception,),
            "assignment_func": validate_gpx,
            "required": False,
            "use_editor": False,
        },
    }

    for attr, config in attr_map.items():
        if attr == "body" and not config["default"]:
            # In case of a `create`, `hike.name` was empty earlier
            config["default"] = f"# {hike.name}  (Markdown supported)"

        # Only prompt for gpx file if none was provided as argument
        if attr != "gpx_xml" or not is_import_from_gpx:
            single_interaction(attr, config, hike)
