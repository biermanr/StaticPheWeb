"""Test synthetic data generation utilities."""

import json
import pathlib

import pytest

from spheweb import chromosomes, legacy_binning, parsing, utils


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


def test_create_synthetic_dataset(tmp_path: pytest.fixture) -> None:
    """Form-A dataset is well-formed and flows through spheweb's binning step."""
    chroms = chromosomes.get_premade_assembly_chroms("hg19")
    pheno_list_path = utils.create_synthetic_dataset(
        chroms, num_phenotypes=3, num_variants=50, out_dir=tmp_path, seed=7
    )

    assert pheno_list_path.exists()
    pheno_list = json.loads(pheno_list_path.read_text())
    assert len(pheno_list) == 3

    for entry in pheno_list:
        assert {"phenocode", "phenostring", "assoc_files"} <= entry.keys()
        assoc_path = pathlib.Path(entry["assoc_files"][0])
        assert assoc_path.exists()

        # The assoc file parses with spheweb's parser and binning (its in-repo
        # port of PheWeb's process step) produces a non-empty Manhattan payload.
        parser = parsing.TabularParser(chroms, assoc_path, delimiter="\t")
        chrom_order = [c.name for c in chroms]
        binned = legacy_binning.LegacyBinner(chrom_order=chrom_order).bin(parser)
        assert binned["variant_bins"] or binned["unbinned_variants"]


def test_create_synthetic_dataset_is_deterministic(tmp_path: pytest.fixture) -> None:
    """The same seed yields byte-identical association files."""
    chroms = chromosomes.get_premade_assembly_chroms("hg19")
    utils.create_synthetic_dataset(chroms, 2, 30, tmp_path / "a", seed=1)
    utils.create_synthetic_dataset(chroms, 2, 30, tmp_path / "b", seed=1)

    for p in range(2):
        a = (tmp_path / "a" / "assoc" / f"pheno{p}.tsv").read_text()
        b = (tmp_path / "b" / "assoc" / f"pheno{p}.tsv").read_text()
        assert a == b
