# StaticPheWeb

StaticPheWeb (`spheweb`) turns Genome-Wide Association Study (GWAS) results into a
**static, server-free website** you can host anywhere that serves files — Amazon S3,
GitHub Pages, or even `python -m http.server`.

[See a live example site →](https://biermanr.github.io/StaticPheWeb/demo/){ .md-button .md-button--primary }

## Why static?

[PheWeb](https://github.com/statgen/pheweb) and
[PheWeb2](https://github.com/GaglianoTaliun-Lab/PheWeb2) are excellent tools for
browsing GWAS results, but they require a **continuously running web server**. For
academic projects the hard part is usually not the server's cost — it is its
**durability and ownership**:

- Servers lapse when a grant ends or the student who set them up moves on.
- Someone has to patch, renew, and babysit the machine for the life of a publication.
- Spinning up a server just so a few collaborators can browse results is a lot of
  overhead for an informal share.

This is a well-known cause of bioinformatics tool link-rot. **Static files have no
owner and no maintenance** — they keep working long after the project wraps up, and
they cost almost nothing to host.

## What you get

`spheweb build static-content` reads a PheWeb-style `pheno-list.json` and emits a small
shared-asset bundle:

```
site/
  index.html        # searchable phenotype index
  spheweb.js        # one shared renderer (no per-phenotype HTML)
  phenotypes.json   # the phenotype list + top hits
  vendor/           # vendored d3
  data/
    <phenotype>.json  # one small, binned payload per phenotype
```

Clicking a phenotype fetches just that phenotype's small JSON and renders an
interactive D3 Manhattan plot client-side — so the site stays small even with many
phenotypes.

## Features

- **No server required** — host the output on any static file host.
- **Interactive Manhattan plots** per phenotype, with variant hover details.
- **Searchable phenotype index** you can filter by name or top-hit position.

Regional association (LocusZoom) and variant/PheWAS views are planned; see the project
[README](https://github.com/biermanr/StaticPheWeb) for the roadmap.

## Next steps

- **[Tutorial](tutorial.md)** — build your first site from synthetic data in four commands.
- **[Using Your Own Data](custom-data.md)** — the input format for real GWAS results.
