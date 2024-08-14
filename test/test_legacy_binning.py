"""Test legacy binning functions."""

from pathlib import Path

import pytest
from spheweb import process


@pytest.mark.slow  # type: ignore
def test_generate_legacy_manhattan_data(tmp_path: Path) -> None:
    """Test generate_legacy_manhattan_data."""
    # data_file = tmp_path / "test.csv"
    # process.generate_legacy_manhattan_data(tmp_path / "test.csv")
    process.generate_legacy_manhattan_json(
        Path("dd_weight_lbs_N-7378.loco.csv"), Path("manhattan.json")
    )
