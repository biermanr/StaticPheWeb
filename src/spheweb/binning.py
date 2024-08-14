"""Classes to bin SNPs from TSV/CSV/MLMA files into windows for plotting."""

from abc import ABC, abstractmethod
from typing import Any

from . import parsing


class Binner(ABC):
    """Abstract base class for binning SNPs into windows for plotting."""

    @abstractmethod
    def bin(self, parser: parsing.Parser) -> dict[str, Any]:
        """Bin the input data file."""
        pass


class WindowBinner(Binner):
    """Simple window-based binning of SNPs."""

    def __init__(self, window_size: int):
        """Initialize the window binner with a window size."""
        self.window_size = window_size

    def bin(self, parser: parsing.Parser) -> dict[str, Any]:
        """Perform the binning of SNPs into windows."""
        return {"TODO": "implement"}
