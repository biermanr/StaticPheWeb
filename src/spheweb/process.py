"""Process input data to fill in HTML and JS templates."""

import importlib.resources
import json
import pathlib
import time
from pathlib import Path
from typing import Any

import fpdf
import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from . import chromosomes, legacy_binning, parsing


def bin_gwas_file(
    data_file: Path, chroms: list[chromosomes.Chrom], delim: str = ","
) -> dict[str, Any]:
    """Parse a single GWAS file and return the legacy binned Manhattan payload.

    The returned dict has ``variant_bins`` and ``unbinned_variants`` keys.
    """
    binner = legacy_binning.LegacyBinner(chrom_order=[c.name for c in chroms])
    parser = parsing.TabularParser(chroms, data_file, delim)
    return binner.bin(parser)


def generate_legacy_manhattan_json(
    data_file: Path, json_out: Path, assembly: str, delim: str = ","
) -> None:
    """Generate data for a Manhattan plot from a data file using legacy PheWeb binning.

    Outputs a JSON file with the binned data.
    """
    chroms = chromosomes.get_premade_assembly_chroms(assembly)
    data = bin_gwas_file(data_file, chroms, delim)

    with json_out.open("w") as json_file:
        json.dump(data, json_file)


def _copy_site_assets(out_dir: Path) -> None:
    """Copy shared static assets (index.html, spheweb.js, vendor/) into out_dir.

    Assets that do not yet exist in the package are silently skipped, so this
    works before and after the shared-renderer assets land.
    """
    templates = importlib.resources.files("spheweb").joinpath("templates")

    for name in ("index.html", "spheweb.js"):
        asset = templates.joinpath(name)
        if asset.is_file():
            out_dir.joinpath(name).write_bytes(asset.read_bytes())

    vendor = templates.joinpath("vendor")
    if vendor.is_dir():
        out_vendor = out_dir / "vendor"
        out_vendor.mkdir(exist_ok=True)
        for entry in vendor.iterdir():
            if entry.is_file():
                out_vendor.joinpath(entry.name).write_bytes(entry.read_bytes())


def build_static_site(
    pheno_list_path: Path,
    assembly: str,
    out_dir: Path,
    delim: str = "\t",
) -> None:
    """Build a static Manhattan site from a PheWeb-style ``pheno-list.json``.

    For each phenotype, bins its association file to ``out_dir/data/<phenocode>.json``,
    writes a small ``phenotypes.json`` index (phenocode, phenostring, top hit),
    and copies the shared site assets. No per-phenotype HTML is produced: the
    single ``index.html`` fetches each phenotype's data on demand.
    """
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    chroms = chromosomes.get_premade_assembly_chroms(assembly)

    with open(pheno_list_path) as f:
        pheno_list = json.load(f)

    index = []
    for entry in pheno_list:
        phenocode = entry["phenocode"]
        assoc_file = Path(entry["assoc_files"][0])
        binned = bin_gwas_file(assoc_file, chroms, delim)

        with data_dir.joinpath(f"{phenocode}.json").open("w") as out_file:
            json.dump(binned, out_file)

        # Top hit = strongest (smallest p-value) variant; the peak variants live
        # in unbinned_variants. No gene annotation: absent from raw GWAS input.
        unbinned = binned["unbinned_variants"]
        top = min(unbinned, key=lambda v: v["pval"]) if unbinned else None
        index.append(
            {
                "phenocode": phenocode,
                "phenostring": entry.get("phenostring", phenocode),
                "top_chrom": top["chrom"] if top else None,
                "top_pos": top["pos"] if top else None,
                "top_pval": top["pval"] if top else None,
            }
        )

    with out_dir.joinpath("phenotypes.json").open("w") as f:
        json.dump(index, f)

    _copy_site_assets(out_dir)


def render_manhattan_plot(out_dir: Path, data: dict[str, Any]) -> None:
    """Use the HTML template and data to generate a new Manhattan HTML file at out_dir."""
    template_path = importlib.resources.files("spheweb").joinpath("templates")

    env = Environment(loader=FileSystemLoader(str(template_path)))
    template = env.get_template("manhattan.html")
    rendered = template.render(data)

    out_dir.mkdir(parents=True, exist_ok=True)
    with out_dir.joinpath("manhattan.html").open("w") as out_file:
        out_file.write(rendered)


def render_manhattan_plot_SVG_from_legacy_JSON_data(
    out_dir: Path, data: dict[str, Any], phenotype: str, assembly: str
) -> None:
    """Create an SVG file for a Manhattan plot using legacy JSON data.

    Goal is to create a .svg file using plotly from the JSON structured data from the legacy
    binning approach which has the following form:

    {
        "variant_bins": [
            {"chrom": "1", "qvals": [3.05, 3.65, 3.95], "qval_extents": [[0.05, 2.85], [3.35, 3.45]], "pos": 1500000},
            {"chrom": "1", "qvals": [3.85], "qval_extents": [[0.05, 3.35]], "pos": 4500000},
            ...
        ],
        "unbinned_variants": [
            {"chrom": "15", "pos": 41521885, "ref": "T", "alt": "C", "pval": 9e-50, "maf": 0.48, ... },
            {"chrom": "15", "pos": 41521682, "ref": "A", "alt": "G", "pval": 1.1e-49, "maf": 0.48, ... },
            ...
        ]
    }
    """
    # TODO this is a hacky way to generate SVGs from legacy JSON data
    out_dir.mkdir(parents=True, exist_ok=True)

    # TODO only using the unbinned variants for now, these are the significant variants
    # TODO need to add the binned variants to the plot, which are the backgrounds
    df = pd.DataFrame(data["unbinned_variants"])
    df["-log10_pval"] = -np.log10(df["pval"])

    # Use chromosome length to determine the position of each variant in "gobal position"
    assembly_chroms = chromosomes.get_premade_assembly_chroms(assembly)
    chrom_colors = {
        0: "#7878ba",
        1: "#004242",
    }
    chrom_order = {chrom.name: i for i, chrom in enumerate(assembly_chroms)}

    chrom_offsets = {}
    running_offset = 0
    chrom_spacing = 50_000_000
    for chrom in assembly_chroms:
        chrom_offsets[chrom.name] = running_offset
        running_offset += chrom.length + chrom_spacing

    df["global_pos_offset"] = df["chrom"].map(chrom_offsets)
    df["global_pos"] = df["pos"] + df["global_pos_offset"]

    plt.figure(figsize=(24, 3))
    plt.scatter(
        df["global_pos"],
        df["-log10_pval"],
        c=df["chrom"].map(chrom_order).mod(2).map(chrom_colors),
        s=0.5,
    )

    # Add rectangles for the binned variants
    for bin_data in data["variant_bins"]:
        chrom = bin_data["chrom"]
        pos = bin_data["pos"]
        qval_extents = bin_data["qval_extents"]

        # Calculate the global position for the bin
        global_pos = pos + chrom_offsets[chrom]

        # Draw rectangles for each binned variants with the qval extents
        for min_qval, max_qval in qval_extents:
            plt.gca().add_patch(
                matplotlib.patches.Rectangle(
                    (global_pos - 0.5, min_qval),
                    1,
                    max_qval - min_qval,
                    color=chrom_colors[chrom_order[chrom] % 2],
                    alpha=0.5,
                    zorder=0,
                )
            )

    plt.axhline(y=-np.log10(5e-8), color="grey", linestyle="--")

    # Adjust the x-ticks to show chromosome positions
    xticks = []
    for chrom in assembly_chroms:
        start_pos = chrom_offsets[chrom.name]
        end_pos = start_pos + chrom.length
        xticks.append((start_pos + end_pos) / 2)

    plt.xticks(xticks, [chrom.name for chrom in assembly_chroms])

    # Adjust y-limits to start at 0
    plt.ylim(bottom=0)

    plt.ylabel("-log10(p-value)")

    plt.title(f"Manhattan Plot for {phenotype}")
    plt.savefig(out_dir.joinpath(f"{phenotype}.svg"), format="svg")
    plt.close()


def render_pdf(
    matrix_tsv_gz_path: pathlib.Path, assembly: str = "canFam4"
) -> pathlib.Path:
    """Write a PDF file from a Matrix TSV GZ file.

    EXPERIMENTAL: the per-phenotype tables and Manhattan inputs are placeholder
    data, not yet wired to the real binned values. Kept as a secondary snapshot
    path only (see plans/v1-static-bundle.md).

    Args:
    ----
        matrix_tsv_gz_path: Path to the TSV file with columns:
            - #chrom
            - pos
            - ref
            - alt
            - rsids
            - nearest_genes
            - pval@1-3-Methylhistidine
            - beta@1-3-Methylhistidine
            - maf@1-3-Methylhistidine
            - pval@creatine
            - beta@creatine
            - maf@creatine
            - ...
        assembly: Chromosome assembly name (e.g. hg19) for the Manhattan plots.

    Returns:
    -------
        Path to the PDF file.

    """
    df = pd.read_csv(matrix_tsv_gz_path, sep="\t")
    unique_phenotypes = set(c.split("@")[1] for c in df.columns if "@" in c)
    phenotypes = sorted(unique_phenotypes)

    pdf_path = matrix_tsv_gz_path.with_suffix(".pdf")

    #############################
    #                           #
    # Overall table of contents #
    #                           #
    #############################
    pdf = fpdf.FPDF()
    pdf.set_font("helvetica", size=14)

    pdf.add_page()
    table_of_contents = pdf.add_link()
    pdf.set_link(table_of_contents, page=pdf.page_no())

    pdf.cell(
        text="Static PheWeb PDF", new_x=fpdf.enums.XPos.LEFT, new_y=fpdf.enums.YPos.NEXT
    )

    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    pdf.cell(
        text=f"This was created on {date}",
        new_x=fpdf.enums.XPos.LEFT,
        new_y=fpdf.enums.YPos.NEXT,
    )

    # Specify the link to the important contents
    about = pdf.add_link()
    phenotypes_table = pdf.add_link()

    pdf.ln(10)
    pdf.cell(
        text="Table of Contents", new_x=fpdf.enums.XPos.LEFT, new_y=fpdf.enums.YPos.NEXT
    )
    pdf.cell(
        text="1. About",
        new_x=fpdf.enums.XPos.LEFT,
        new_y=fpdf.enums.YPos.NEXT,
        link=about,
        border=1,
    )
    pdf.cell(
        text="2. Phenotypes",
        new_x=fpdf.enums.XPos.LEFT,
        new_y=fpdf.enums.YPos.NEXT,
        link=phenotypes_table,
        border=1,
    )

    #############################
    #                           #
    #           About           #
    #                           #
    #############################
    pdf.add_page()
    pdf.set_link(about, page=pdf.page_no())
    pdf.cell(
        text="About this PDF", new_x=fpdf.enums.XPos.LEFT, new_y=fpdf.enums.YPos.NEXT
    )
    pdf.cell(
        text="This is a static PheWeb that has a subset of the full functionality of Pheweb",
        new_x=fpdf.enums.XPos.LEFT,
        new_y=fpdf.enums.YPos.NEXT,
    )
    pdf.cell(
        text="Return to the table of contents",
        new_x=fpdf.enums.XPos.LEFT,
        new_y=fpdf.enums.YPos.NEXT,
        link=table_of_contents,
        border=1,
    )

    #############################
    #                           #
    #      Phenotypes table     #
    #                           #
    #############################
    pdf.add_page()
    pdf.set_link(phenotypes_table, page=pdf.page_no())
    pdf.set_font("helvetica", size=10)

    pdf.cell(
        text="List of Phenotypes",
        new_x=fpdf.enums.XPos.LEFT,
        new_y=fpdf.enums.YPos.NEXT,
    )
    pdf.cell(
        text="Return to the table of contents",
        new_x=fpdf.enums.XPos.LEFT,
        new_y=fpdf.enums.YPos.NEXT,
        link=table_of_contents,
        border=1,
    )

    # Pre-specify the links to the manhattan plot pages which will be bound to pages later
    manhattan_links = {phenotype: pdf.add_link() for phenotype in phenotypes}

    # Table of phenotypes
    pdf.set_font("helvetica", size=8)
    with pdf.table() as table:
        head = table.row()
        head.cell("Category")
        head.cell("Phenotype name")
        head.cell("Top variant")
        head.cell("P-value")
        head.cell("MAF")
        head.cell("Neareast Gene")

        for phenotype in phenotypes:
            row = table.row()
            row.cell("Uncategorized")  # NOTE
            pdf.set_text_color(0, 0, 255)
            row.cell(text=phenotype, link=manhattan_links[phenotype])
            pdf.set_text_color(0, 0, 0)
            row.cell("rsid???")  # NOTE
            row.cell("1.0")  # NOTE
            row.cell("0.5")  # NOTE
            row.cell("Gene???")  # NOTE

    #############################
    #                           #
    #      Phenotypes pages     #
    #                           #
    #############################
    for phenotype in phenotypes:
        pdf.add_page()
        pdf.set_link(manhattan_links[phenotype])
        pdf.cell(text="Link to first page", link=table_of_contents)
        pdf.cell(200, 10, f"Manhattan plot for {phenotype}")

        # TODO hacky way to generate SVGs from legacy JSON data for now
        data = {
            "variant_bins": [
                {
                    "chrom": "1",
                    "qvals": [3.05, 3.65, 3.95],
                    "qval_extents": [[0.05, 2.85], [3.35, 3.45]],
                    "pos": 1500000,
                },
                {
                    "chrom": "1",
                    "qvals": [3.85],
                    "qval_extents": [[0.05, 3.35]],
                    "pos": 4500000,
                },
            ],
            "unbinned_variants": [
                {
                    "chrom": "15",
                    "pos": 41521885,
                    "ref": "T",
                    "alt": "C",
                    "pval": 9e-50,
                    "maf": 0.48,
                },
                {
                    "chrom": "15",
                    "pos": 41521682,
                    "ref": "A",
                    "alt": "G",
                    "pval": 1.1e-49,
                    "maf": 0.48,
                },
            ],
        }

        render_manhattan_plot_SVG_from_legacy_JSON_data(
            out_dir=pathlib.Path("svgs"),
            data=data,
            phenotype=phenotype,
            assembly=assembly,
        )
        pdf.image(f"svgs/{phenotype}.svg", x=10, y=20, w=180)

    pdf.output(pdf_path)

    return pdf_path
