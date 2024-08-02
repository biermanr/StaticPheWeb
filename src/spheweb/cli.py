"""Command line interface for spheweb."""

import click
import jinja2  # NOTE, move this to a different file


@click.group()
def cli() -> None:
    """CLI group to add subcommands for spheweb."""
    pass


@cli.command()
@click.argument("input_fname", type=click.Path(exists=True))
def parse(input_fname: click.Path) -> None:
    """Parse inputs to generate a static pheweb visualization."""
    click.echo(click.format_filename(input_fname))

    # Create an pheweb.html file which contains the HTML/CSS/JS/DATA for the pheweb
    # visualization using jinja2 with a template

    # NOTE TODO: learn about frozen-flask and flask_flatpages as a way to generate static pages
    environment = jinja2.Environment()
    template = environment.get_template("template.html")
    template.render(name="John Doe")
