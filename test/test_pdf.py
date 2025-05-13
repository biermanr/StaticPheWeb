"""Test the PDF generation functionality."""

import pathlib

import pytest
from spheweb import chromosomes, process, utils


@pytest.mark.slow  # type: ignore[misc]
def test_write_pdf_from_matrix(tmpdir: pytest.fixture) -> None:
    """Test the write_pdf_from_matrix function."""
    matrix_gz_path = pathlib.Path(tmpdir) / "synthetic_matrix.tsv.gz"
    sep = "\t"
    num_phenotypes = 2
    num_variants = 100
    chroms = chromosomes.get_premade_assembly_chroms("hg19")
    utils.create_matrix_gz_file(
        chroms, num_phenotypes, num_variants, matrix_gz_path, sep=sep
    )
    assert matrix_gz_path.exists()

    pdf_path = process.render_pdf(matrix_gz_path)
    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
