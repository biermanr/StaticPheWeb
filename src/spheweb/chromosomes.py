"""Chromosome classes and functions."""


class Chrom:
    """Simple class for representing a chromosome."""

    def __init__(self, organism: str, name: str, order: int) -> None:
        """Initialize the chromosome object."""
        self.organism = organism
        self.name = name
        self.order = order

    def __eq__(self, other: object) -> bool:
        """Compare the chromosome objects for equality."""
        if not isinstance(other, Chrom):
            return NotImplemented

        if self.organism != other.organism:
            return False

        return self.name == other.name and self.order == other.order

    def __lt__(self, other: object) -> bool:
        """Compare the chromosome objects for less-than."""
        if not isinstance(other, Chrom):
            return NotImplemented

        if self.organism != other.organism:
            return NotImplemented

        return self.order < other.order

    def __hash__(self) -> int:
        """Hash the chromosome object."""
        return hash((self.organism, self.name, self.order))


def specify_chroms(organism: str, chroms: list[str]) -> list[Chrom]:
    """Create a list of Chrom objects for the specified organism and chromosome names ordered as provided."""
    return [Chrom(organism, name, i) for i, name in enumerate(chroms, 1)]


def get_premade_organism_chroms(organism: str) -> list[Chrom]:
    """Get a list of Chrom objects for the specified organism."""
    if organism == "human":
        return [
            Chrom(organism, "1", 1),
            Chrom(organism, "2", 2),
            Chrom(organism, "3", 3),
            Chrom(organism, "4", 4),
            Chrom(organism, "5", 5),
            Chrom(organism, "6", 6),
            Chrom(organism, "7", 7),
            Chrom(organism, "8", 8),
            Chrom(organism, "9", 9),
            Chrom(organism, "10", 10),
            Chrom(organism, "11", 11),
            Chrom(organism, "12", 12),
            Chrom(organism, "13", 13),
            Chrom(organism, "14", 14),
            Chrom(organism, "15", 15),
            Chrom(organism, "16", 16),
            Chrom(organism, "17", 17),
            Chrom(organism, "18", 18),
            Chrom(organism, "19", 19),
            Chrom(organism, "20", 20),
            Chrom(organism, "21", 21),
            Chrom(organism, "22", 22),
            Chrom(organism, "X", 39),
            Chrom(organism, "Y", 40),
            Chrom(organism, "MT", 41),
        ]
    elif organism == "dog":
        return [
            Chrom(organism, "1", 1),
            Chrom(organism, "2", 2),
            Chrom(organism, "3", 3),
            Chrom(organism, "4", 4),
            Chrom(organism, "5", 5),
            Chrom(organism, "6", 6),
            Chrom(organism, "7", 7),
            Chrom(organism, "8", 8),
            Chrom(organism, "9", 9),
            Chrom(organism, "10", 10),
            Chrom(organism, "11", 11),
            Chrom(organism, "12", 12),
            Chrom(organism, "13", 13),
            Chrom(organism, "14", 14),
            Chrom(organism, "15", 15),
            Chrom(organism, "16", 16),
            Chrom(organism, "17", 17),
            Chrom(organism, "18", 18),
            Chrom(organism, "19", 19),
            Chrom(organism, "20", 20),
            Chrom(organism, "21", 21),
            Chrom(organism, "22", 22),
            Chrom(organism, "23", 23),
            Chrom(organism, "24", 24),
            Chrom(organism, "25", 25),
            Chrom(organism, "26", 26),
            Chrom(organism, "27", 27),
            Chrom(organism, "28", 28),
            Chrom(organism, "29", 29),
            Chrom(organism, "30", 30),
            Chrom(organism, "31", 31),
            Chrom(organism, "32", 32),
            Chrom(organism, "33", 33),
            Chrom(organism, "34", 34),
            Chrom(organism, "35", 35),
            Chrom(organism, "36", 36),
            Chrom(organism, "37", 37),
            Chrom(organism, "38", 38),
            Chrom(organism, "X", 39),
            Chrom(organism, "Y", 40),
            Chrom(organism, "MT", 41),
        ]
    else:
        raise ValueError(f"Unknown organism: {organism}")
