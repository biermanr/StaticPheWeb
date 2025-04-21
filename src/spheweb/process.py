"""Process input data to fill in HTML and JS templates."""

import importlib.resources
import json
import pathlib
from pathlib import Path
from typing import Any

import pandas as pd
from fpdf import FPDF
from jinja2 import Environment, FileSystemLoader

from . import chromosomes, legacy_binning, parsing


def generate_legacy_manhattan_json(
    data_file: Path, json_out: Path, delim: str = ","
) -> None:
    """Generate data for a Manhattan plot from a data file using legacy PheWeb binning."""
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

    pdf = FPDF()
    pdf.set_font("helvetica", size=14)
    pdf.add_page()
    table_of_contents = pdf.add_link()

    # Pre-specify the links to the pages which will be bound to pages later
    manhattan_links = {phenotype: pdf.add_link() for phenotype in phenotypes}

    # Table of phenotypes
    with pdf.table() as table:
        for phenotype in phenotypes:
            row = table.row()
            row.cell(phenotype, link=manhattan_links[phenotype])

    # Pages of Manhattan plots (TODO just repeating the same PNG for now)
    for phenotype in phenotypes:
        pdf.add_page()
        pdf.set_link(manhattan_links[phenotype], page=pdf.page_no())
        pdf.cell(text="Link to first page", link=table_of_contents)
        pdf.cell(200, 10, f"Manhattan plot for {phenotype}")
        pdf.image("example_manhattan.png", x=10, y=20, w=180)

    pdf.output(pdf_path)

    return pdf_path
