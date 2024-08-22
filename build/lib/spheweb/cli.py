"""Command line interface for spheweb."""

import json  # NOTE, move somewhere else
from pathlib import Path

import click

from . import __version__, chromosomes, parsing, process


@click.group()
@click.version_option(version=__version__)
def spheweb() -> None:
    """CLI group to add subcommands for spheweb."""
    pass


@spheweb.command()
@click.argument("out_dir", type=Path)
@click.argument("json_file", type=Path)
def build(out_dir, json_file) -> None:
    """Parse inputs to generate a static pheweb visualization."""
    # Create an pheweb.html file which contains the HTML/CSS/JS/DATA for the pheweb
    # visualization using jinja2 with a template

    with open(json_file) as f:
        data = json.load(f)

    process.render_manhattan_plot(out_dir, {"data": data})


@spheweb.command()
@click.argument("tabular_file", type=Path)
@click.option("--delim", "-d", default=",", type=str)
def validate_input(tabular_file, delim) -> None:
    """Validate format of input CSV file, or use --delim to specify other tabular format."""
    chroms = chromosomes.get_premade_organism_chroms("dog")
    num_lines = sum(1 for _ in parsing.TabularParser(chroms, tabular_file, delim))
    click.echo(
        f"File {tabular_file} with {num_lines:,} successfully parsed, file is valid!"
    )
