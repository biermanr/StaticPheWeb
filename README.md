# StaticPheWeb

StaticPheWeb is a tool written in python that allows users to provide their Genome-Wide Association
Study (GWAS) data to generate single-file static websites with interactive displays. With StaticPheWeb, you can easily
create interactive and informative visualizations of your GWAS results, making
it easier for others to explore and understand your research findings.

## Features

- **Easy Integration**: StaticPheWeb generates static website files from your GWAS results, allowing you to showcase your GWAS data without the need for complex server-side setups.
- **Interactive Visualizations**: D3 Manhattan plots per phenotype, with a searchable phenotype index. (Regional association and QQ views are planned.)
- **Data Exploration**: Hover variants for details and filter the phenotype list by name or top-hit position.

## Getting Started

StaticPheWeb turns a PheWeb-style `pheno-list.json` (mapping phenotypes to GWAS
association files) into a static, server-free site: one `index.html` plus a small
`data/<phenotype>.json` per phenotype, rendered client-side. Host it anywhere that
serves files (S3, GitHub Pages, `python -m http.server`).

The walkthrough below is deterministic — run it with [uv](https://docs.astral.sh/uv/)
and you'll get the same site every time.

```bash
# 1. Install dependencies into a local environment
uv sync

# 2. Generate a synthetic PheWeb-style dataset (pheno-list.json + assoc files).
#    --seed makes the output reproducible.
uv run spheweb synthetic-dataset --ref hg19 --out demo --num-phenos 4 --seed 0

# 3. Build the static site
uv run spheweb build static-content --phenos demo/pheno-list.json --ref hg19 --out site

# 4. Serve it and open http://127.0.0.1:8000 in a browser.
#    Note: the site fetches per-phenotype JSON, so it must be served over HTTP
#    (it will not work by double-clicking index.html via file://).
python -m http.server 8000 --directory site
```

To use your own data, replace step 2 with a `pheno-list.json` of the form:

```json
[
  {"phenocode": "T2D", "phenostring": "Type 2 Diabetes", "assoc_files": ["t2d.tsv"]}
]
```

where each association file is a CSV/TSV with at least `chrom`, `pos`, `ref`, `alt`,
and `pval` columns (common aliases such as `#chrom`, `p-value`, `beta`, `maf` are
accepted). Pass `--ref` for your assembly (`hg19`, `hg38`/`grch38`, `canFam4`); run
`uv run spheweb list-ref-genomes` to see the supported assemblies.

## Contributing

We welcome contributions from the community to make StaticPheWeb even better. If
you have any ideas, bug reports, or feature requests, please open an issue or
submit a pull request.

## License

StaticPheWeb is released under the [MIT License](https://opensource.org/licenses/MIT). Feel free to use, modify, and distribute this tool for both personal and commercial purposes.
