"""Utility functions for PheWeb."""

import gzip
import json
import pathlib
import random
from collections.abc import Iterator

from . import chromosomes, variant

# Nucleotides used when drawing synthetic ref/alt alleles.
NUCLEOTIDES = ("A", "C", "G", "T")


def _synthetic_variants(
    rng: random.Random,
    chroms: list[chromosomes.Chrom],
    num_variants: int,
) -> Iterator[variant.Variant]:
    """Yield seeded, realistic Variants in valid (chrom, strictly-increasing pos) order.

    Most variants are null (uniform p-value); a small fraction are injected as
    genome-wide-significant hits so the resulting Manhattan plot has real peaks.
    Constructing each row through the Variant model guarantees the output parses.
    """
    for chrom in chroms:
        pos = 0
        for _ in range(num_variants):
            pos += rng.randint(1, 1000)  # keep positions strictly increasing
            ref = rng.choice(NUCLEOTIDES)
            alt = rng.choice([n for n in NUCLEOTIDES if n != ref])

            if rng.random() < 0.02:
                pval = 10 ** (-rng.uniform(8, 30))  # occasional strong hit
            else:
                pval = max(rng.random(), 1e-300)  # null, never exactly 0

            yield variant.Variant(
                chrom=chrom.name,
                pos=pos,
                ref=ref,
                alt=alt,
                pval=pval,
                maf=round(rng.uniform(0.01, 0.5), 6),
                alt_allele_freq=round(rng.uniform(0.0, 1.0), 6),
                effect_size=round(rng.gauss(0.0, 0.1), 6),
            )


def create_phenotype_GWAS_file(
    chroms: list[chromosomes.Chrom],
    num_variants: int,
    output_path: pathlib.Path,
    sep: str = ",",
    seed: int = 0,
) -> None:
    """Create a synthetic single-phenotype GWAS file (deterministic given ``seed``).

    Columns: chrom, pos, ref, alt, pval, maf, alt_allele_freq, effect_size.
    """
    header = list(variant.Variant.model_fields.keys())
    rng = random.Random(seed)

    with open(output_path, "w") as f:
        f.write(sep.join(header) + "\n")
        for v in _synthetic_variants(rng, chroms, num_variants):
            # write fields in header order
            f.write(sep.join(str(getattr(v, field)) for field in header) + "\n")


def create_synthetic_dataset(
    chroms: list[chromosomes.Chrom],
    num_phenotypes: int,
    num_variants: int,
    out_dir: pathlib.Path,
    seed: int = 0,
    sep: str = "\t",
) -> pathlib.Path:
    """Create a PheWeb-style raw input set (Form A): pheno-list.json + assoc files.

    Writes one association file per phenotype under ``out_dir/assoc/`` and a
    ``pheno-list.json`` referencing them. Each assoc file has the columns
    ``chrom pos ref alt pval beta maf`` — names recognised by both spheweb's
    ``TabularParser`` and upstream PheWeb. Deterministic given ``seed``.

    Returns the path to the written ``pheno-list.json``.
    """
    out_dir = pathlib.Path(out_dir)
    assoc_dir = out_dir / "assoc"
    assoc_dir.mkdir(parents=True, exist_ok=True)

    assoc_header = ["chrom", "pos", "ref", "alt", "pval", "beta", "maf"]
    pheno_list = []

    for p in range(num_phenotypes):
        phenocode = f"pheno{p}"
        assoc_path = assoc_dir / f"{phenocode}.tsv"
        rng = random.Random(f"{seed}:{p}")  # distinct but reproducible per phenotype

        with open(assoc_path, "w") as f:
            f.write(sep.join(assoc_header) + "\n")
            for v in _synthetic_variants(rng, chroms, num_variants):
                row = [v.chrom, v.pos, v.ref, v.alt, v.pval, v.effect_size, v.maf]
                f.write(sep.join(str(x) for x in row) + "\n")

        pheno_list.append(
            {
                "phenocode": phenocode,
                "phenostring": f"Synthetic phenotype {p}",
                "assoc_files": [str(assoc_path)],
            }
        )

    pheno_list_path = out_dir / "pheno-list.json"
    with open(pheno_list_path, "w") as f:
        json.dump(pheno_list, f, indent=2)

    return pheno_list_path


def create_matrix_gz_file(
    chroms: list[chromosomes.Chrom],
    num_phenotypes: int,
    num_variants: int,
    output_path: pathlib.Path,
    sep: str = "\t",
    seed: int = 0,
) -> None:
    """Create a synthetic PheWeb matrix.tsv.gz file (Form B), deterministic given ``seed``.

    Columns: #chrom, pos, ref, alt, rsids, nearest_genes, then a
    (pval@<pheno>, beta@<pheno>, maf@<pheno>) triple per phenotype.
    """
    header = [
        "#chrom",
        "pos",
        "ref",
        "alt",
        "rsids",
        "nearest_genes",
    ]

    for i in range(num_phenotypes):
        header.append(f"pval@phenotype{i}")
        header.append(f"beta@phenotype{i}")
        header.append(f"maf@phenotype{i}")

    rng = random.Random(seed)

    with gzip.open(output_path, "wt") as f:
        f.write(sep.join(header) + "\n")
        for chrom in chroms:
            pos = 0
            for _ in range(num_variants):
                pos += rng.randint(1, 1000)
                ref = rng.choice(NUCLEOTIDES)
                alt = rng.choice([n for n in NUCLEOTIDES if n != ref])
                fields = [
                    chrom.name,
                    str(pos),
                    ref,
                    alt,
                    f"rs{chrom.name}_{pos}",
                    f"gene{chrom.name}_{pos}",
                ]
                for _p in range(num_phenotypes):
                    pval = max(rng.random(), 1e-300)
                    fields.append(str(pval))
                    fields.append(str(round(rng.gauss(0.0, 0.1), 6)))
                    fields.append(str(round(rng.uniform(0.01, 0.5), 6)))
                f.write(sep.join(fields) + "\n")
