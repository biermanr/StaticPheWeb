"""Test synthetic data generation utilities."""

import pytest

from spheweb import chromosomes, parsing, utils


def test_create_phenotype_GWAS_file(tmp_path: pytest.fixture) -> None:
    """Test the create_phenotype_GWAS_file function."""
    chroms = chromosomes.get_premade_assembly_chroms("canFam4")
    num_variants = 100
    output_path = tmp_path / "synthetic_gwas.tsv"
    sep = "\t"

    utils.create_phenotype_GWAS_file(chroms, num_variants, output_path, sep=sep)

    assert output_path.exists()
    assert output_path.suffix == ".tsv"

    # Check that the synthetic file can be parsed correctly
    parser = parsing.TabularParser(chroms, output_path, delimiter=sep)

    for variant in parser:
        assert variant.chrom in [chrom.name for chrom in chroms]


def test_create_matrix_gz_file(tmp_path: pytest.fixture) -> None:
    """Test the create_matrix_gz_file function."""
    chroms = chromosomes.get_premade_assembly_chroms("canFam4")
    num_phenotypes = 2
    num_variants = 100
    output_path = tmp_path / "synthetic_matrix.tsv.gz"
    sep = "\t"

    utils.create_matrix_gz_file(
        chroms, num_phenotypes, num_variants, output_path, sep=sep
    )

    assert output_path.exists()
