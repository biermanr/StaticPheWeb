"""Test rendering of HTML templates."""

from pathlib import Path
from typing import Any

import html5lib
import spheweb


def test_render_manhattan(tmpdir: Any) -> None:
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

    spheweb.process.render_manhattan_plot(d, {"data": data})

    parser = html5lib.HTMLParser(strict=True)
    parser.parse(d.joinpath("manhattan.html").read_text())
