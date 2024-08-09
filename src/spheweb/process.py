"""Process input data to fill in HTML and JS templates."""

import importlib.resources
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader  # type: ignore


def render_manhattan_plot(out_dir: Path, data: Dict[str, Any]) -> None:
    """Use the HTML template and data to generate a new Manhattan HTML file at out_dir."""
    template_path = importlib.resources.files("spheweb").joinpath("templates")

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template("manhattan.html")
    rendered = template.render(data)

    out_dir.mkdir(parents=True, exist_ok=True)
    with out_dir.joinpath("manhattan.html").open("w") as out_file:
        out_file.write(rendered)
