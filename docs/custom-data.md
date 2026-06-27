# Using Your Own Data

To build a site from real GWAS results, replace the synthetic-data step of the
[tutorial](tutorial.md) with your own `pheno-list.json`.

## The `pheno-list.json` file

StaticPheWeb uses the same PheWeb-style phenotype list: a JSON array where each entry
maps a phenotype to one or more association files.

```json
[
  {"phenocode": "T2D", "phenostring": "Type 2 Diabetes", "assoc_files": ["t2d.tsv"]},
  {"phenocode": "BMI", "phenostring": "Body Mass Index",  "assoc_files": ["bmi.tsv"]}
]
```

- `phenocode` — short identifier; also used as the data filename (`data/<phenocode>.json`).
- `phenostring` — human-readable label shown in the index.
- `assoc_files` — path(s) to the association summary-statistics file(s) for that phenotype.

## Association file format

Each association file is a CSV/TSV with **at least** these columns:

| Column | Required | Common aliases |
| ------ | -------- | -------------- |
| `chrom` | yes | `#chrom`, `chr` |
| `pos`   | yes | `position`, `bp` |
| `ref`   | yes | `reference` |
| `alt`   | yes | `alternate` |
| `pval`  | yes | `p-value`, `p`, `pvalue` |
| `beta`  | no  | `effect_size` |
| `maf`   | no  | `minor_allele_frequency` |

Variants should be sorted by chromosome and position.

## Building

```bash
uv run spheweb build static-content \
  --phenos pheno-list.json \
  --ref hg19 \
  --out site
```

- `--ref` selects the genome assembly. Supported values include `hg19`, `hg38`
  (`grch38`), and `canFam4`. Run `uv run spheweb list-ref-genomes` to see the full list.
- `--delim` / `-d` sets the association-file delimiter (defaults to tab).

## Validating inputs

Before a full build you can check that a single file parses cleanly:

```bash
uv run spheweb validate-input your_file.tsv --ref hg19
```

This reports the number of valid variants or the first formatting error it hits.
