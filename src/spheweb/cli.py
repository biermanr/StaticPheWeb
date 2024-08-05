"""Command line interface for spheweb."""

import click

from . import __version__


@click.group()
@click.version_option(version=__version__)
def spheweb():
    """CLI group to add subcommands for spheweb."""
    pass


@spheweb.command()
# @click.argument("input_fname", type=click.Path(exists=True))
def parse():
    """Parse inputs to generate a static pheweb visualization."""
    # click.echo(click.format_filename(input_fname))
    print("Made it here!")

    # Create an pheweb.html file which contains the HTML/CSS/JS/DATA for the pheweb
    # visualization using jinja2 with a template
