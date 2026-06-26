"""Best-effort parity check: synthetic Form-A input is accepted by upstream PheWeb.

spheweb's ``LegacyBinner`` is the in-repo port of PheWeb's process/binning step.
This test cross-checks the synthetic dataset against the *real* tool when it is
available, and skips otherwise so CI without the heavy upstream stack (PheWeb +
htslib) stays green. Developers with ``pheweb`` and ``tabix``/``bgzip`` installed
get an actual end-to-end compatibility assertion.
"""

import shutil
import subprocess

import pytest

from spheweb import chromosomes, utils

pytestmark = pytest.mark.slow


def test_synthetic_dataset_accepted_by_pheweb(tmp_path: pytest.fixture) -> None:
    """`pheweb process` accepts the generated pheno-list.json + assoc files."""
    if shutil.which("pheweb") is None:
        pytest.skip("pheweb not installed; skipping upstream parity check")
    if shutil.which("tabix") is None or shutil.which("bgzip") is None:
        pytest.skip("htslib (tabix/bgzip) required by `pheweb process` is unavailable")

    chroms = chromosomes.get_premade_assembly_chroms("hg19")
    pheno_list = utils.create_synthetic_dataset(
        chroms, num_phenotypes=2, num_variants=300, out_dir=tmp_path, seed=1
    )

    # Minimal PheWeb data directory: a config and the generated pheno-list.json
    # (whose assoc_files are absolute paths into tmp_path).
    data_dir = tmp_path / "pheweb"
    data_dir.mkdir()
    (data_dir / "config.py").write_text("hg_build_number = 19\n")
    shutil.copy(pheno_list, data_dir / "pheno-list.json")

    # A clean exit means upstream's parser accepted the synthetic association files.
    result = subprocess.run(
        ["pheweb", "process"],
        cwd=data_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (data_dir / "generated-by-pheweb").is_dir()
