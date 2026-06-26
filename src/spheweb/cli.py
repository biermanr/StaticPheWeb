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


@spheweb.group()
def build() -> None:
    """Build static outputs (interactive site, single page, or PDF) from GWAS data."""


@build.command("static-content")
@click.option(
    "--phenos",
    type=Path,
    required=True,
    help="PheWeb-style pheno-list.json mapping phenotypes to association files.",
)
@click.option(
    "--ref", "-r", type=str, required=True, help="Chromosome assembly, such as hg19."
)
@click.option(
    "--out", type=Path, required=True, help="Output directory for the static site."
)
@click.option(
    "--delim", "-d", default="\t", type=str, help="Association-file delimiter."
)
def build_static_content(phenos, ref, out, delim) -> None:
    """Build a searchable static site with per-phenotype Manhattan plots."""
    process.build_static_site(phenos, ref, out, delim=delim)
    click.echo(f"Static site written to {out}")


@build.command("single", hidden=True)
@click.argument("out_dir", type=Path)
@click.argument("json_file", type=Path)
def build_single(out_dir, json_file) -> None:
    """Render a single Manhattan page from one binned JSON file."""
    with open(json_file) as f:
        data = json.load(f)

    process.render_manhattan_plot(out_dir, {"data": data})


@build.command("pdf", hidden=True)
@click.argument("matrix_tar_gz", type=Path)
@click.option(
    "--ref", "-r", type=str, default="canFam4", help="Chromosome assembly, such as hg19."
)
def build_pdf(matrix_tar_gz, ref) -> None:
    """Render an (experimental) PDF snapshot report from a matrix.tsv.gz."""
    process.render_pdf(matrix_tar_gz, assembly=ref)


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


@spheweb.command()
@click.option(
    "--ref",
    type=str,
    required=True,
    help="Reference genome, such as hg19, grch38, or canFam4.",
)
@click.option(
    "--out",
    type=Path,
    required=True,
    help="Output directory for the synthetic dataset.",
)
@click.option("--num-phenos", type=int, default=3, help="Number of phenotypes.")
@click.option("--num-variants", type=int, default=200, help="Variants per chromosome.")
@click.option("--seed", type=int, default=0, help="Seed for reproducible output.")
def synthetic_dataset(ref, out, num_phenos, num_variants, seed) -> None:
    """Create a PheWeb-style dataset (pheno-list.json + per-phenotype assoc files)."""
    try:
        chroms = chromosomes.get_premade_assembly_chroms(ref)
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    pheno_list_path = utils.create_synthetic_dataset(
        chroms, num_phenos, num_variants, out, seed=seed
    )

    click.echo(f"Synthetic dataset created, pheno-list at {pheno_list_path}")


@spheweb.command(hidden=True)
@click.argument("out_dir", type=Path)
@click.argument("json_file", type=Path)
@click.option(
    "--ref", "-r", type=str, required=True, help="Chromosome assembly, such as hg19."
)
def svg_manhattan(out_dir, json_file, ref) -> None:
    """Create a Manhattan plot SVG from legacy JSON data."""
    with open(json_file) as f:
        data = json.load(f)

    process.render_manhattan_plot_SVG_from_legacy_JSON_data(
        out_dir,
        data,
        "test_phenotype",
        assembly=ref,
    )


@spheweb.command(hidden=True)
@click.argument("matrix_tar_gz", type=Path)
def matrix_to_sqlite(matrix_tar_gz) -> None:
    """Convert a matrix.tar.gz file to a SQLite database."""
    utils.convert_tsv_gz_to_normalized_sqlite(matrix_tar_gz)
