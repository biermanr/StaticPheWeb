"""Test rendering of HTML templates."""

from pathlib import Path

import html5lib
import pytest

from spheweb import process


def test_render_manhattan(tmpdir: pytest.fixture) -> None:
    """Test the render_manhattan function with mock data."""
    d = Path(tmpdir)

    # Mock data, single variant and single bin
    # TODO make pydantic classes for plot/table data
    data = {
        "unbinned_variants": [
            {
                "alt": "C",
                "beta": -0.15,
                "chrom": "15",
                "maf": 0.48,
                "nearest_genes": "IGF1",
                "num_significant_in_peak": 290,
                "peak": True,
                "pos": 41521885,
                "pval": 9e-50,
                "effect_size": -0.15,
                "ref": "T",
                "rsids": "",
            },
        ],
        "variant_bins": [
            {
                "chrom": "1",
                "color": "rgb(120,120,186)",
                "pos": 1500000,
                "qval_extents": [
                    [0.05, 2.85],
                    [3.35, 3.45],
                ],
                "qvals": [3.05, 3.65, 3.95],
            }
        ],
    }

    process.render_manhattan_plot(d, {"data": data})

    parser = html5lib.HTMLParser(strict=True)
    parser.parse(d.joinpath("manhattan.html").read_text())


@pytest.mark.slow  # type: ignore[misc]
def test_render_manhattan_plot_SVG_from_legacy_JSON_data(
    tmpdir: pytest.fixture,
) -> None:
    """Test the render_manhattan_plot_SVG_from_legacy_JSON_data function with mock data."""
    out_dir = Path(tmpdir)

    data = {
        "unbinned_variants": [
            {
                "alt": "C",
                "beta": -0.15,
                "chrom": "15",
                "maf": 0.48,
                "nearest_genes": "IGF1",
                "num_significant_in_peak": 290,
                "peak": True,
                "pos": 41521885,
                "pval": 9e-50,
                "effect_size": -0.15,
                "ref": "T",
                "rsids": "",
            },
        ],
        "variant_bins": [
            {
                "chrom": "1",
                "color": "rgb(120,120,186)",
                "pos": 1500000,
                "qval_extents": [
                    [0.05, 2.85],
                    [3.35, 3.45],
                ],
                "qvals": [3.05, 3.65, 3.95],
            }
        ],
    }

    process.render_manhattan_plot_SVG_from_legacy_JSON_data(
        out_dir,
        data,
        phenotype="test",
    )

    assert out_dir.joinpath("test.svg").exists()
