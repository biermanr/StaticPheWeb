"""Process input data to fill in HTML and JS templates."""

import importlib.resources
import json
import pathlib
import time
from pathlib import Path
from typing import Any

import fpdf
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from . import chromosomes, legacy_binning, parsing


def generate_legacy_manhattan_json(
    data_file: Path, json_out: Path, delim: str = ","
) -> None:
    """Generate data for a Manhattan plot from a data file using legacy PheWeb binning.

    Outputs a JSON file with the binned data.
    """
    binner = legacy_binning.LegacyBinner()
    chroms = chromosomes.get_premade_organism_chroms("dog")
    parser = parsing.TabularParser(chroms, data_file, delim)
    data = binner.bin(parser)

    with json_out.open("w") as json_file:
        json.dump(data, json_file)


def render_manhattan_plot(out_dir: Path, data: dict[str, Any]) -> None:
    """Use the HTML template and data to generate a new Manhattan HTML file at out_dir."""
    template_path = importlib.resources.files("spheweb").joinpath("templates")

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template("manhattan.html")
    rendered = template.render(data)

    out_dir.mkdir(parents=True, exist_ok=True)
    with out_dir.joinpath("manhattan.html").open("w") as out_file:
        out_file.write(rendered)


def render_manhattan_plot_SVG_from_legacy_JSON_data(
    out_dir: Path, data: dict[str, Any], phenotype: str
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
    # svg_path = out_dir.joinpath(f"{phenotype}.svg")

    pass


def render_pdf(matrix_tsv_gz_path: pathlib.Path) -> pathlib.Path:
    """Write a PDF file from a Matrix TSV GZ file.

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
        border=True,
    )
    pdf.cell(
        text="2. Phenotypes",
        new_x=fpdf.enums.XPos.LEFT,
        new_y=fpdf.enums.YPos.NEXT,
        link=phenotypes_table,
        border=True,
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
        border=True,
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
        border=True,
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
    # TODO just repeating the same PNG for now
    for phenotype in phenotypes:
        pdf.add_page()
        pdf.set_link(manhattan_links[phenotype], page=pdf.page_no())
        pdf.cell(text="Link to first page", link=table_of_contents)
        pdf.cell(200, 10, f"Manhattan plot for {phenotype}")
        pdf.image("example_manhattan.png", x=10, y=20, w=180)

    pdf.output(pdf_path)

    return pdf_path
