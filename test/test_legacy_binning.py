"""Test legacy binning functions."""

from pathlib import Path

import pytest
from spheweb import process


@pytest.mark.slow  # type: ignore
def test_generate_legacy_manhattan_data(tmp_path: Path) -> None:
    """Test generate_legacy_manhattan_data against a small validated input."""
    data_file = Path("test/pheno_data.csv")
    out_file = tmp_path / "manhattan.json"
    ground_truth = Path("test/pheno_manhattan.json")

    process.generate_legacy_manhattan_json(
        data_file,
        out_file,
    )

    with open(out_file) as f, open(ground_truth) as g:
        assert f.read() == g.read()
