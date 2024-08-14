"""Process input data to fill in HTML and JS templates."""

import importlib.resources
import json
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from . import chromosomes, legacy_binning, parsing


def generate_legacy_manhattan_json(data_file: Path, json_out: Path) -> None:
    """Generate data for a Manhattan plot from a data file using legacy PheWeb binning."""
    binner = legacy_binning.LegacyBinner()
    chroms = chromosomes.get_premade_organism_chroms("dog")
    parser = parsing.TabularParser(chroms, data_file)
    data = binner.bin(parser)

    with json_out.open("w") as json_file:
        json.dump(data, json_file)


def render_manhattan_plot(out_dir: Path, data: Dict[str, Any]) -> None:
    """Use the HTML template and data to generate a new Manhattan HTML file at out_dir."""
    template_path = importlib.resources.files("spheweb").joinpath("templates")

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template("manhattan.html")
    rendered = template.render(data)

    out_dir.mkdir(parents=True, exist_ok=True)
    with out_dir.joinpath("manhattan.html").open("w") as out_file:
        out_file.write(rendered)
