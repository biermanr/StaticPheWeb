"""Tests for the chromosomes module."""

import pytest
from spheweb import chromosomes


def test_chrom_comparison() -> None:
    """Test comparing chromosomes."""
    human_chr1 = chromosomes.Chrom("human", "1", 1)
    human_chr2 = chromosomes.Chrom("human", "2", 2)
    human_chrX = chromosomes.Chrom("human", "X", 23)
    human_chrY = chromosomes.Chrom("human", "X", 24)
    human_chrM = chromosomes.Chrom("human", "M", 25)

    dog_chr3 = chromosomes.Chrom("dog", "3", 3)
    dog_chr4 = chromosomes.Chrom("dog", "4", 4)
    dog_chrX = chromosomes.Chrom("dog", "X", 39)
    dog_chrY = chromosomes.Chrom("dog", "Y", 40)
    dog_chrM = chromosomes.Chrom("dog", "M", 41)

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

    # Comparing equality of chromosomes from different organisms should return False
    assert human_chr1 != dog_chr3

    # Comparing order of chromosomes from different organisms should raise TypeError
    with pytest.raises(TypeError):
        assert human_chr1 < dog_chr3

    with pytest.raises(TypeError):
        assert human_chr2 <= dog_chr4

    with pytest.raises(TypeError):
        assert human_chrX > dog_chrX

    with pytest.raises(TypeError):
        assert human_chrY >= dog_chrY


def test_specify_chroms() -> None:
    """Test generating list of chromosomes by specifying organism and chromosome names."""
    c1, c2, c3 = chromosomes.specify_chroms(organism="test", chroms=["1", "2", "M"])

    assert isinstance(c1, chromosomes.Chrom)
    assert c1.organism == "test"
    assert c1.name == "1"

    assert isinstance(c2, chromosomes.Chrom)
    assert c2.organism == "test"
    assert c2.name == "2"

    assert isinstance(c3, chromosomes.Chrom)
    assert c3.organism == "test"
    assert c3.name == "M"


@pytest.mark.parametrize("organism", ["human", "dog"])  # type: ignore[misc]
def test_premade_chromosomes(organism: str) -> None:
    """Test that the premade chromosomes are correct."""
    human_chroms = chromosomes.get_premade_organism_chroms(organism)
    for chrom in human_chroms:
        assert isinstance(chrom, chromosomes.Chrom)
        assert chrom.organism == organism


def test_missing_premade_chromosomes() -> None:
    """Test that an error is raised for missing premade chromosomes."""
    with pytest.raises(ValueError) as e:
        chromosomes.get_premade_organism_chroms("missing")
        assert "Missing chromosomes for organism" in str(e.value)
