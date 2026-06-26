"""Tests for spheweb CLI."""

from click.testing import CliRunner

from spheweb import __version__, chromosomes, utils
from spheweb.cli import spheweb as cli

runner = CliRunner()


def test_version():
    """Test the version command."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"spheweb, version {__version__}\n"


def test_parse_help():
    """Test the help message for the parse command."""
    result = runner.invoke(cli, ["build", "--help"])
    assert result.exit_code == 0


def test_validate_input_help():
    """Test the help message for the validate_input command."""
    result = runner.invoke(cli, ["validate-input", "--help"])
    assert result.exit_code == 0


def test_list_ref_genomes_help():
    """Test the help message for the list_ref_genomes command."""
    result = runner.invoke(cli, ["list-ref-genomes", "--help"])
    assert result.exit_code == 0


def test_list_ref_genomes():
    """Test the list_ref_genomes command."""
    result = runner.invoke(cli, ["list-ref-genomes"])
    assert result.exit_code == 0
    assert "Available reference genomes:" in result.output

    for ref in chromosomes.premade_refs.keys():
        assert ref in result.output


def test_synthetic_gwas_unknown_ref():
    """Test the synthetic data generation command with an unknown reference genome."""
    result = runner.invoke(
        cli,
        [
            "synthetic-gwas",
            "--ref",
            "unknown_ref",
            "--output",
            "synthetic_data.tsv",
        ],
    )
    assert result.exit_code != 0
    assert "Error: Unknown" in result.output


def test_synthetic_gwas_data(tmp_path):
    """Test the synthetic data generation command."""
    result = runner.invoke(cli, ["synthetic-gwas", "--help"])
    assert result.exit_code == 0

    output_path = tmp_path / "synthetic_data.tsv"

    result = runner.invoke(
        cli,
        [
            "synthetic-gwas",
            "--ref",
            "canFam4",
            "--output",
            output_path,
        ],
    )
    assert result.exit_code == 0
    assert output_path.exists()


def test_validate_input(tmp_path):
    """Test the validate_input command."""
    data_path = tmp_path / "synthetic_data.tsv"
    chroms = chromosomes.get_premade_assembly_chroms("canFam4")

    utils.create_phenotype_GWAS_file(
        chroms,
        num_variants=100,
        output_path=data_path,
        sep="\t",
    )

    result = runner.invoke(
        cli,
        [
            "validate-input",
            "--ref",
            "canFam4",
            "--delim",
            "\t",
            str(data_path),
        ],
    )
    assert result.exit_code == 0
    assert "successfully parsed" in result.output
