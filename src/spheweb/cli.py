"""Command line interface for spheweb."""

import json  # NOTE, move somewhere else
from pathlib import Path

import click

from . import __version__, chromosomes, parsing, process, utils


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
def list_ref_genomes() -> None:
    """List available reference genomes."""
    click.echo("Available reference genomes:")
    for ref in chromosomes.premade_refs.keys():
        click.echo(f"- {ref}")


@spheweb.command()
@click.argument("tabular_file", type=Path)
@click.option(
    "--ref",
    "-r",
    type=str,
    help="Chromosome assembly to use, such as hg19",
    required=True,
)
@click.option("--delim", "-d", default=",", type=str)
def validate_input(tabular_file, ref, delim) -> None:
    """Validate format of tabular format GWAS data file."""
    chroms = chromosomes.get_premade_assembly_chroms(ref)
    num_lines = sum(1 for _ in parsing.TabularParser(chroms, tabular_file, delim))
    click.echo(
        f"File {tabular_file} with {num_lines:,} successfully parsed, file is valid!"
    )


@spheweb.command()
@click.option(
    "--ref",
    type=str,
    required=True,
    help="Reference genome, such as hg19, grch38, or canFam4.",
)
@click.option(
    "--output",
    type=Path,
    required=True,
    help="Output file path for the synthetic data.",
)
def synthetic_gwas(ref, output) -> None:
    """Create a synthetic GWAS data file for a single phenotype."""
    try:
        chroms = chromosomes.get_premade_assembly_chroms(ref)
    except ValueError as e:
        click.echo(f"Error: {e}")
        click.Abort()

    num_variants = 100
    utils.create_phenotype_GWAS_file(chroms, num_variants, output, sep="\t")

    click.echo(f"Synthetic data created at {output}")


@spheweb.command(hidden=True)
@click.argument("phenotype_gwas", type=Path)
def svg_manhattan(phenotype_gwas) -> None:
    """Create a Manhattan plot SVG from a phenotype GWAS file."""
    pass


@spheweb.command(hidden=True)
@click.argument("matrix_tar_gz", type=Path)
def matrix_to_sqlite(matrix_tar_gz) -> None:
    """Convert a matrix.tar.gz file to a SQLite database."""
    utils.convert_tsv_gz_to_normalized_sqlite(matrix_tar_gz)


@spheweb.command(hidden=True)
@click.argument("matrix_tar_gz", type=Path)
def matrix_to_pdf(matrix_tar_gz) -> None:
    """Convert a matrix.tar.gz file to a PDF report."""
    process.render_pdf(matrix_tar_gz)
