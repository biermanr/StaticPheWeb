"""Module for parsing data files into Variant models."""

from abc import ABC, abstractmethod
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
