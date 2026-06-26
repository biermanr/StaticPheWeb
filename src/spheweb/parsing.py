"""Module for parsing data files into Variant models."""

import csv
from collections.abc import Iterator
from pathlib import Path

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
        if sorted(chroms) != chroms:
            raise ValueError("Chromosomes are not in order")

        self.chroms = chroms

        # Initialize the generator of Variant models for __iter__ and __next__
        self.variants = self.generate_variants()
        self.chrom_name_order = {c.name: c.order for c in self.chroms}
        self.prev_chrom_name = self.chroms[0].name
        self.prev_chrom_order = self.chroms[0].order
        self.prev_pos = -1

    def generate_variants(self) -> Iterator[variant.Variant]:  # type: ignore[empty-body]
        """Generate an iterator of Variant models.

        This method MUST be implemented by sub-classes.
        It should yield Variant models one at a time.
        This method gets called by __next__ via self.variants.
        """
        pass

    def __iter__(self) -> Iterator[variant.Variant]:
        """Prepare for iteration.

        Sub-classes should not need to override this method.
        """
        return self

    def __next__(self) -> variant.Variant:
        """Return the next variant.

        Ensure that the chromosomes and positions are valid and in order.
        Sub-classes should NOT override this method or risk forgetting
        to validate the chromosomes and positions ordering.
        """
        try:
            v = next(self.variants)
        except StopIteration as exc:
            raise exc

        # TODO try and move chrom validation to pydantic
        if v.chrom not in self.chrom_name_order:
            raise ValueError(
                f"Observed chromosome: {v.chrom} not in specified chromosomes {self.chrom_name_order.keys()}"
            )
        if self.chrom_name_order[v.chrom] < self.prev_chrom_order:
            raise ValueError(
                f"Invalid chromosome order: {v.chrom} observed after {self.prev_chrom_name}"
            )
        if v.pos < 0:
            raise ValueError(f"Invalid position: {v.pos}")
        if self.prev_chrom_name == v.chrom and self.prev_pos == v.pos:
            raise ValueError(f"Duplicate variant position: {v.chrom}:{v.pos}")
        if self.prev_chrom_name == v.chrom and self.prev_pos > v.pos:
            raise ValueError(
                f"Invalid position order: {v.pos} comes after {self.prev_pos} on {v.chrom}"
            )

        self.prev_chrom_name = v.chrom
        self.prev_chrom_order = self.chrom_name_order[v.chrom]
        self.prev_pos = v.pos
        return v


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
                yield variant.Variant.model_validate(row)
