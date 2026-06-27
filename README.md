# StaticPheWeb

StaticPheWeb (`spheweb`) turns Genome-Wide Association Study (GWAS) results into a
**static, server-free website** you can host anywhere that serves files — Amazon S3,
GitHub Pages, or `python -m http.server`. No Flask server to set up, pay for, or maintain.

- 📖 **Documentation:** <https://biermanr.github.io/StaticPheWeb/>
- 🔬 **Live demo:** <https://biermanr.github.io/StaticPheWeb/demo/>

## Quick start

```bash
uv sync

# Generate a reproducible synthetic dataset (pheno-list.json + assoc files)
uv run spheweb synthetic-dataset --ref hg19 --out demo --num-phenos 4 --seed 0

# Build the static site
uv run spheweb build static-content --phenos demo/pheno-list.json --ref hg19 --out site

# Serve it (the pages fetch JSON over HTTP, so file:// won't work)
python -m http.server 8000 --directory site
```

See the [tutorial](https://biermanr.github.io/StaticPheWeb/tutorial/) for a full
walkthrough and [Using Your Own Data](https://biermanr.github.io/StaticPheWeb/custom-data/)
for the input format.

## Why static?

PheWeb and PheWeb2 are great, but they require a continuously running web server. For
academic projects the hard part is the server's **durability and ownership** — it lapses
when grants end or people move on, which is a common cause of tool link-rot. Static files
have no owner and no maintenance, and cost almost nothing to host. See the
[docs](https://biermanr.github.io/StaticPheWeb/) for more.

## Contributing

Contributions are welcome — please open an issue or pull request with ideas, bug
reports, or feature requests.

## License

StaticPheWeb is released under the [MIT License](https://opensource.org/licenses/MIT).
