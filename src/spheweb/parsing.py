"""Module for parsing data files into Variant models."""

import csv
from pathlib import Path
from typing import Iterator

from . import chromosomes, variant


class Parser:
    """Class for parsing data files.

    Generates iterable of Variant pydantic models
    And checks for valid chromosome and position order.
    """

    def __init__(self, chroms: list[chromosomes.Chrom]) -> None:
        """Initialize the parser with a list of valid chromosomes.

        Sub-classes should use super().__init__(chroms) to set the valid chromosomes
        after initializing their own attributes.
        """
        if len(chroms) == 0:
            raise ValueError("No chromosomes provided")
        if len(chroms) != len(set(chroms)):
            raise ValueError("Duplicate chromosomes in the list")
        self.chroms = chroms

    def generate_variants(self) -> Iterator[variant.Variant]:  # type: ignore
        """Generate an iterator of Variant models.

        This method must be implemented by sub-classes.
        """
        pass

    def __iter__(self) -> Iterator[variant.Variant]:
        """Parse the input data file and return an iterable.

        Ensure that the chromosomes and positions are valid and in order.
        Sub-classes should NOT override this method or risk forgetting
        to validate the chromosomes and positions ordering.
        """
        # TODO try and move chrom validation to pydantic
        chrom_name_order = {c.name: c.order for c in self.chroms}
        prev_chrom_name = self.chroms[0].name
        prev_chrom_order = self.chroms[0].order
        prev_pos = 0
        for v in self.generate_variants():
            if v.chrom not in chrom_name_order:
                raise ValueError(
                    f"Observed chromosome: {v.chrom} not in specified chromosomes {chrom_name_order.keys()}"
                )
            if chrom_name_order[v.chrom] < prev_chrom_order:
                raise ValueError(
                    f"Invalid chromosome order: {v.chrom} observed after {prev_chrom_name}"
                )
            if v.pos < 0:
                raise ValueError(f"Invalid position: {v.pos}")
            if prev_chrom_name == v.chrom and prev_pos == v.pos:
                raise ValueError(f"Duplicate variant position: {v.chrom}:{v.pos}")
            if prev_chrom_name == v.chrom and prev_pos > v.pos:
                raise ValueError(
                    f"Invalid position order: {v.pos} comes after {prev_pos} on {v.chrom}"
                )

            prev_chrom_name = v.chrom
            prev_chrom_order = chrom_name_order[v.chrom]
            prev_pos = v.pos
            yield v


class TabularParser(Parser):
    """Parser for CSV/TSV/etc files."""

    def __init__(
        self, chroms: list[chromosomes.Chrom], file_path: Path, delimiter: str = ","
    ) -> None:
        """Initialize the parser with the path to the tabular file and delimiter.

        Make sure to call super().__init__(chroms) to set the valid chromosomes.
        """
        self.file_path = file_path
        self.delimiter = delimiter
        super().__init__(chroms)

    def generate_variants(self) -> Iterator[variant.Variant]:
        """Parse the input CSV file and return a generator of Variant."""
        with open(self.file_path) as csvfile:
            for row in csv.DictReader(csvfile, delimiter=self.delimiter):
                yield variant.Variant(**row)
