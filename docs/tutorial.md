# Tutorial

This walkthrough builds a complete StaticPheWeb site from synthetic data. It is
**deterministic** — run it with [uv](https://docs.astral.sh/uv/) and the `--seed` flag
and you get the same site every time, which makes it easy to follow for a human or an
AI agent.

The result is exactly what powers the
[live demo](https://biermanr.github.io/StaticPheWeb/demo/).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed.
- A clone of the repository:

  ```bash
  git clone https://github.com/biermanr/StaticPheWeb
  cd StaticPheWeb
  ```

## 1. Install dependencies

```bash
uv sync
```

## 2. Generate a synthetic dataset

This creates a PheWeb-style `pheno-list.json` plus one association file per phenotype.
`--seed` makes the output reproducible.

```bash
uv run spheweb synthetic-dataset --ref hg19 --out demo --num-phenos 4 --seed 0
```

## 3. Build the static site

```bash
uv run spheweb build static-content --phenos demo/pheno-list.json --ref hg19 --out site
```

## 4. Serve it locally

```bash
python -m http.server 8000 --directory site
```

Open <http://127.0.0.1:8000> and click a phenotype to see its Manhattan plot.

!!! note "Why a server for a *static* site?"
    The pages fetch per-phenotype JSON over HTTP, so opening `index.html` directly from
    disk (`file://`) is blocked by the browser. Any static file host works —
    `python -m http.server` locally, or S3 / GitHub Pages in production.

## 5. Publish

The `site/` directory is self-contained. Upload it to any static host:

- **Amazon S3** — enable static website hosting and `aws s3 sync site/ s3://your-bucket/`.
- **GitHub Pages** — commit `site/` (or deploy it via GitHub Actions, as this project does).
- **Anywhere else** that serves files over HTTP.

Next: point it at [your own GWAS data](custom-data.md).
