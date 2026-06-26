"""Classes to bin SNPs from TSV/CSV/MLMA files into windows for Manhattan style plotting."""

from abc import ABC, abstractmethod
from typing import Any

from . import parsing


class Binner(ABC):
    """Abstract base class for binning SNPs into windows for plotting."""

    @abstractmethod
    def bin(self, parser: parsing.Parser) -> dict[str, Any]:
        """Bin the input data file.

        This method should be implemented by subclasses to perform the actual binning.
        """
        pass
