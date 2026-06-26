"""Tests for the utils module."""

import pytest

from spheweb import utils


def test_convert_tsv_gz_to_sqlite(matrix_gz_path: pytest.fixture) -> None:
    """Test converting a TSV file to a normalized SQLite database.

    Note that this is likely going to get removed since SQLite was determined
    to likely not to be a good choice for storing the PheWeb data.
    """
    sqlite_path = utils.convert_tsv_gz_to_sqlite(matrix_gz_path)
    assert sqlite_path.exists()


def test_convert_tsv_gz_to_normalized_sqlite(matrix_gz_path: pytest.fixture) -> None:
    """Test converting a TSV file to a normalized SQLite database.

    Note that this is likely going to get removed since SQLite was determined
    to likely not to be a good choice for storing the PheWeb data.
    """
    sqlite_path = utils.convert_tsv_gz_to_normalized_sqlite(matrix_gz_path)
    assert sqlite_path.exists()
