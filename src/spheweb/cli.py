"""Command line interface for spheweb."""

from pathlib import Path

import click

from . import __version__, process


@click.group()
@click.version_option(version=__version__)
def spheweb() -> None:
    """CLI group to add subcommands for spheweb."""
    pass


@spheweb.command()
@click.argument("out_dir", type=Path)
def build(out_dir) -> None:
    """Parse inputs to generate a static pheweb visualization."""
    # Create an pheweb.html file which contains the HTML/CSS/JS/DATA for the pheweb
    # visualization using jinja2 with a template

    data = {
        "2023-01-01": 100,
        "2023-02-01": 20,
        "2023-03-01": 30,
        "2023-04-01": 40,
        "2023-05-01": 50,
        "2023-06-01": 60,
        "2023-07-01": 70,
        "2023-08-01": 80,
        "2023-09-01": 90,
        "2023-10-01": 100,
        "2023-11-01": 90,
        "2023-12-01": 80,
        "2024-01-01": 70,
    }

    process.render_html(
        out_dir, {"name": "Jake", "data": data}
    )  # NOTE fake hardcoded data for now
