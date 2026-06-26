"""Test the static-site builder."""

import json

import html5lib
import pytest

from spheweb import chromosomes, process, utils

# Guards the size-wall fix: per-phenotype payload must stay small.
MAX_PHENO_JSON_BYTES = 150_000


def test_build_static_site(tmp_path: pytest.fixture) -> None:
    """build_static_site emits per-phenotype data + an index, with no per-pheno HTML."""
    chroms = chromosomes.get_premade_assembly_chroms("hg19")
    pheno_list = utils.create_synthetic_dataset(
        chroms, num_phenotypes=3, num_variants=50, out_dir=tmp_path / "input", seed=3
    )

    site = tmp_path / "site"
    process.build_static_site(pheno_list, assembly="hg19", out_dir=site, delim="\t")

    # Index lists every phenotype with a resolvable data file.
    index_path = site / "phenotypes.json"
    assert index_path.exists()
    index = json.loads(index_path.read_text())
    assert len(index) == 3

    for entry in index:
        assert {"phenocode", "phenostring", "top_chrom", "top_pos", "top_pval"} == set(
            entry.keys()
        )
        assert (site / "data" / f"{entry['phenocode']}.json").exists()

    # The whole point of the shared-asset model: no per-phenotype HTML.
    assert list(site.glob("data/*.json"))
    assert not list(site.rglob("data/*.html"))

    # Shared assets are copied once.
    assert (site / "index.html").exists()
    assert (site / "spheweb.js").exists()
    assert (site / "vendor" / "d3.min.js").exists()
    assert (site / "vendor" / "underscore-min.js").exists()
    assert (site / "vendor" / "d3-tip.min.js").exists()

    # The single entry point is valid HTML5.
    html5lib.HTMLParser(strict=True).parse((site / "index.html").read_text())

    # Each per-phenotype payload stays under the size-wall budget.
    for data_file in site.glob("data/*.json"):
        assert data_file.stat().st_size < MAX_PHENO_JSON_BYTES
