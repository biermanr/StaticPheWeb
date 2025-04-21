"""Configuration for pytest."""

import pathlib
import random
import typing

import pandas as pd
import pytest


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
    columns = [
        "#chrom",
        "pos",
        "ref",
        "alt",
        "rsids",
        "nearest_genes",
    ]
    num_phenotypes = 30
    pheno_columns = [
        f"{kind}@pheno{pheno}"
        for pheno in range(1, num_phenotypes + 1)
        for kind in ["pval", "beta", "maf"]
    ]

    columns = columns + pheno_columns

    data: dict[str, list[typing.Any]] = {col: [] for col in columns}
    bases = {"A", "C", "G", "T"}
    num_loci = 100
    for i in range(num_loci):
        data["#chrom"].append("chr1")
        data["pos"].append(i)
        ref = random.choice(list(bases))
        alt = random.choice(list(bases - {ref}))
        data["ref"].append(ref)
        data["alt"].append(alt)
        data["rsids"].append(f"rs{i}")
        data["nearest_genes"].append(f"gene{i}")

        for pheno in range(1, num_phenotypes + 1):
            # Random pval, beta, maf values
            data[f"pval@pheno{pheno}"].append(random.uniform(0, 1))
            data[f"beta@pheno{pheno}"].append(random.uniform(-1, 1))
            data[f"maf@pheno{pheno}"].append(random.uniform(0, 0.5))

    df = pd.DataFrame(data)

    tsv_file = tmp_path / "matrix.tsv.gz"
    df.to_csv(tsv_file, sep="\t", index=False, compression="gzip")

    return pathlib.Path(tsv_file)
