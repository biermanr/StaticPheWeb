"""Test the PDF generation functionality."""

import pytest
from spheweb import process


@pytest.mark.slow  # type: ignore[misc]
def test_write_pdf_from_matrix(matrix_gz_path: pytest.fixture) -> None:
    """Test the write_pdf_from_matrix function."""
    pdf_path = process.render_pdf(matrix_gz_path)
    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
