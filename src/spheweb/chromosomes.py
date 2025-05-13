"""Chromosome classes and functions."""

import functools
from types import NotImplementedType


@functools.total_ordering
class Chrom:
    """Simple class for representing a chromosome."""

    def __init__(self, assembly: str, name: str, order: int, length: int) -> None:
        """Initialize the chromosome object."""
        self.assembly = assembly
        self.name = name
        self.order = order
        self.length = length

    def __repr__(self) -> str:
        """Return a string representation of the chromosome object."""
        return f"Chrom(assembly={self.assembly}, name={self.name}, order={self.order}, length={self.length})"

    def __eq__(self, other: object) -> bool | NotImplementedType:
        """Compare the chromosome objects for equality."""
        if not isinstance(other, Chrom):
            return NotImplemented

        if self.assembly != other.assembly:
            return False

        return (
            self.name == other.name
            and self.order == other.order
            and self.length == other.length
        )

    def __lt__(self, other: object) -> bool | NotImplementedType:
        """Compare the chromosome objects for less-than."""
        if not isinstance(other, Chrom):
            return NotImplemented

        if self.assembly != other.assembly:
            return NotImplemented

        return self.order < other.order

    def __hash__(self) -> int:
        """Hash the chromosome object."""
        return hash((self.assembly, self.name, self.order))

    def __len__(self) -> int:
        """Return the length of the chromosome."""
        return self.length


def create_chroms_from_lengths_dict(
    assembly: str, chrom_lengths: dict[str, int]
) -> list[Chrom]:
    """Create a list of Chrom objects from an ordered dictionary of chromosome lengths.

    Args:
    ----
        assembly (str): The assembly name.
        chrom_lengths (dict[str, int]): A dictionary of chromosome names and their lengths.

    Returns:
    -------
        list[Chrom]: A list of Chrom objects.

    Example:
    -------
        >>> chrom_lengths = {'1': 249250621, '2': 243199373, '3': 198022430}
        >>> create_chroms_from_lengths('hg19', chrom_lengths)
        [
            Chrom(assembly='hg19', name='1', order=1, length=249250621),
            Chrom(assembly='hg19', name='2', order=2, length=243199373),
            Chrom(assembly='hg19', name='3', order=3, length=198022430)
        ]

    """
    chroms = [
        Chrom(assembly, name, i + 1, length)
        for i, (name, length) in enumerate(chrom_lengths.items())
    ]
    return chroms


# TODO refactor, maybe make a class for "RefGenome" or something
# TODO add a function to get the chromosome lengths from UCSC or Ensembl
# TODO add a function to get the chromosome lengths from a file
premade_refs = {
    "hg19": create_chroms_from_lengths_dict(
        "hg19",
        {
            "1": 249_250_621,
            "2": 243_199_373,
            "3": 198_022_430,
            "4": 191_154_276,
            "5": 180_915_260,
            "6": 171_115_067,
            "7": 159_138_663,
            "8": 146_364_022,
            "9": 141_213_431,
            "10": 135_534_747,
            "11": 135_006_516,
            "12": 133_851_895,
            "13": 115_169_878,
            "14": 107_349_540,
            "15": 102_531_392,
            "16": 90_354_753,
            "17": 81_195_210,
            "18": 78_077_248,
            "19": 59_128_983,
            "20": 63_025_520,
            "21": 48_129_895,
            "22": 51_304_566,
            "X": 155_270_560,
            "Y": 59_373_566,
            "MT": 16_569,
        },
    ),
    "hg38": create_chroms_from_lengths_dict(
        "hg38",
        {
            "1": 248_956_422,
            "2": 242_193_529,
            "3": 198_295_559,
            "4": 190_214_555,
            "5": 181_538_259,
            "6": 170_805_979,
            "7": 159_345_973,
            "8": 145_138_636,
            "9": 138_394_717,
            "10": 133_797_422,
            "11": 135_086_622,
            "12": 133_275_309,
            "13": 114_364_328,
            "14": 107_043_718,
            "15": 101_991_189,
            "16": 90_338_345,
            "17": 83_257_441,
            "18": 80_373_285,
            "19": 58_617_616,
            "20": 64_444_167,
            "21": 46_709_983,
            "22": 50_818_468,
            "X": 156_040_895,
            "Y": 57_227_415,
            "MT": 16_569,
        },
    ),
    "canFam4": create_chroms_from_lengths_dict(
        "canFam4",
        {
            "1": 122_014_068,
            "2": 82_037_489,
            "3": 94_329_250,
            "4": 87_912_527,
            "5": 88_913_986,
            "6": 80_213_190,
            "7": 80_419_774,
            "8": 73_585_679,
            "9": 60_315_500,
            "10": 69_219_345,
            "11": 72_832_428,
            "12": 72_300_020,
            "13": 62_895_387,
            "14": 60_430_354,
            "15": 64_389_122,
            "16": 54_556_944,
            "17": 63_738_581,
            "18": 54_357_284,
            "19": 52_989_165,
            "20": 57_984_708,
            "21": 50_232_922,
            "22": 61_822_301,
            "23": 52_413_914,
            "24": 46_832_179,
            "25": 51_908_704,
            "26": 38_725_074,
            "27": 46_280_981,
            "28": 41_264_955,
            "29": 40_893_792,
            "30": 40_067_686,
            "31": 39_086_971,
            "32": 41_857_359,
            "33": 31_422_675,
            "34": 51_113_282,
            "35": 26_040_529,
            "36": 30_723_464,
            "37": 31_754_289,
            "38": 23_973_277,
            "X": 108_808_365,
            "MT": 16_735,
        },
    ),
}


def get_premade_assembly_chroms(assembly: str) -> list[Chrom]:
    """Get a list of Chrom objects for the specified organism."""
    if assembly.lower() in {"hg19", "grch37"}:
        return premade_refs["hg19"]

    elif assembly.lower() in {"hg38", "grch38"}:
        return premade_refs["hg38"]

    elif assembly.lower() == "canfam4":
        return premade_refs["canFam4"]

    else:
        raise ValueError(f"Unknown assembly: {assembly} for premade chromosomes.")
