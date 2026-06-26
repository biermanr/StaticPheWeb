"""Configuration for pytest."""

import pathlib

import pytest

from spheweb import chromosomes, utils


def pytest_addoption(parser):  # type: ignore[no-untyped-def]
    """Create a command line option to run slow tests."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):  # type: ignore[no-untyped-def]
    """Skip slow tests if --run-slow is not provided."""
    if config.getoption("--run-slow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture  # type: ignore[misc]
def matrix_gz_path(tmp_path: pytest.fixture) -> pathlib.Path:
    """Pytest fixture to create a temporary matrix.tsv.gz file.

    Create a temporary TSV file to represent the matrix.tsv.gz file
    from PheWeb with the following columns
    #chrom, pos, ref, alt, rsids, nearest_genes, pval@glucose, beta@glucose, maf@glucose, pval@creatine, beta@creatine, maf@creatine,...
    """
    tsv_file = tmp_path / "matrix.tsv.gz"
    utils.create_matrix_gz_file(
        chromosomes.get_premade_assembly_chroms("hg19"),
        num_phenotypes=2,
        num_variants=100,
        output_path=tsv_file,
        sep="\t",
    )
    return pathlib.Path(tsv_file)
