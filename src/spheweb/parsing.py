"""Module for parsing data files into Variant models."""

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from . import variant


class Parser(ABC):
    """Abstract base class for parsing data files.

    Callable, generates iterable of Variant pydantic models.
    """

    @abstractmethod
    def __iter__(self) -> Iterable[variant.Variant]:
        """Parse the input data file and return an iterable."""
        pass


class TabularParser(Parser):
    """Parser for CSV/TSV/etc files."""

    def __init__(self, file_path: Path, delimiter: str = ",") -> None:
        """Initialize the parser with the path to the tabular file and delimiter."""
        self.file_path = file_path
        self.delimiter = delimiter

    def __iter__(self) -> Iterable[variant.Variant]:
        """Parse the input CSV file and return a generator of Variant."""
        with open(self.file_path) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=self.delimiter)
            for row in reader:
                yield variant.Variant(**row)
