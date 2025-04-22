"""Tests for the chromosomes module."""

import pytest
from spheweb import chromosomes


def test_chrom_comparison() -> None:
    """Test comparing chromosomes."""
    human_chr1 = chromosomes.Chrom("human", "1", 1, 9000)
    human_chr2 = chromosomes.Chrom("human", "2", 2, 8000)
    human_chrX = chromosomes.Chrom("human", "X", 23, 7000)
    human_chrY = chromosomes.Chrom("human", "X", 24, 6000)
    human_chrM = chromosomes.Chrom("human", "M", 25, 5000)

    dog_chr3 = chromosomes.Chrom("dog", "3", 3, 7000)
    dog_chr4 = chromosomes.Chrom("dog", "4", 4, 6000)
    dog_chrX = chromosomes.Chrom("dog", "X", 39, 1000)
    dog_chrY = chromosomes.Chrom("dog", "Y", 40, 500)
    dog_chrM = chromosomes.Chrom("dog", "M", 41, 400)

    assert human_chr1 < human_chr2
    assert human_chr2 < human_chrX
    assert human_chrX < human_chrY
    assert human_chrY < human_chrM

    assert human_chr2 > human_chr1
    assert human_chrX > human_chr2
    assert human_chrY > human_chrX
    assert human_chrM > human_chrY

    assert dog_chr3 <= dog_chr4
    assert dog_chr4 <= dog_chrX
    assert dog_chrX <= dog_chrY
    assert dog_chrY <= dog_chrM

    assert dog_chr4 >= dog_chr3
    assert dog_chrX >= dog_chr4
    assert dog_chrY >= dog_chrX
    assert dog_chrM >= dog_chrY

    # Comparing non-chromosome object should return TypeError
    with pytest.raises(TypeError):
        assert human_chr1 < 1

    # Equality comparison of chromosome with non-chromosome object will return False
    # I wanted it to return NotImplemented for this case,
    # but it seems it will try left.__eq__(right) first, and if that returns NotImplemented,
    # it will try right.__eq__(left) which will be False if right is a built-in type.
    # this doesn't seem to be the case for the other comparison operators
    assert human_chr1 != 1

    # Comparing equality of chromosomes from different assembly should return False
    assert human_chr1 != dog_chr3

    # Comparing order of chromosomes from different assembly should raise TypeError
    with pytest.raises(TypeError):
        assert human_chr1 < dog_chr3

    with pytest.raises(TypeError):
        assert human_chr2 <= dog_chr4

    with pytest.raises(TypeError):
        assert human_chrX > dog_chrX

    with pytest.raises(TypeError):
        assert human_chrY >= dog_chrY


def test_create_chroms_from_lengths_dict() -> None:
    """Test generating list of chromosomes by specifying assembly and chromosome names."""
    c1, c2, c3 = chromosomes.create_chroms_from_lengths_dict(
        assembly="test", chrom_lengths={"1": 9000, "2": 8000, "M": 1000}
    )

    assert isinstance(c1, chromosomes.Chrom)
    assert c1.assembly == "test"
    assert c1.name == "1"

    assert isinstance(c2, chromosomes.Chrom)
    assert c2.assembly == "test"
    assert c2.name == "2"

    assert isinstance(c3, chromosomes.Chrom)
    assert c3.assembly == "test"
    assert c3.name == "M"


@pytest.mark.parametrize("assembly", ["hg19", "hg38", "grch37", "grch38", "canfam4"])  # type: ignore[misc]
def test_premade_chromosomes(assembly: str) -> None:
    """Test that the premade chromosomes are correct."""
    human_chroms = chromosomes.get_premade_assembly_chroms(assembly)
    for chrom in human_chroms:
        assert isinstance(chrom, chromosomes.Chrom)
        assert chrom.assembly == assembly


def test_missing_premade_chromosomes() -> None:
    """Test that an error is raised for missing premade chromosomes."""
    with pytest.raises(ValueError) as e:
        chromosomes.get_premade_assembly_chroms("missing")
        assert "Missing chromosomes for assembly" in str(e.value)
