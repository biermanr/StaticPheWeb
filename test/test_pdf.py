"""Test the PDF generation functionality."""

import pathlib

from spheweb import utils


def test_write_pdf_from_matrix(matrix_gz_path: pathlib.Path) -> None:
    """Test the write_pdf_from_matrix function."""
    pdf_path = utils.write_pdf_from_matrix(matrix_gz_path)
    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
