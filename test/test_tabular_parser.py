"""Test CSV parser."""

from pathlib import Path

import pytest
from spheweb import chromosomes, parsing


@pytest.fixture  # type: ignore
def chroms() -> list[chromosomes.Chrom]:
    """Return a list of Chrom objects."""
    return [
        chromosomes.Chrom(organism="test", name="1", order=1),
        chromosomes.Chrom(organism="test", name="2", order=2),
    ]


def test_good_csv_parse(tmp_path: Path, chroms: pytest.fixture) -> None:
    """Test CSVParser."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "chromosome,position,ref,alt,pval\n" "1,1000,A,T,0.01\n" "2,2000,C,G,0.23\n"
    )

    for i, v in enumerate(parsing.TabularParser(chroms, csv_file)):
        if i == 0:
            assert v.chrom == "1"
            assert v.pos == 1000
            assert v.ref == "A"
            assert v.alt == "T"
            assert v.pval == 0.01

        if i == 1:
            assert v.chrom == "2"
            assert v.pos == 2000
            assert v.ref == "C"
            assert v.alt == "G"
            assert v.pval == 0.23

        if i > 1:
            raise AssertionError("Too many rows in test.csv")


def test_good_tsv_parse(tmp_path: Path, chroms: pytest.fixture) -> None:
    """Test CSVParser with a TSV."""
    tsv_file = tmp_path / "test.tsv"
    tsv_file.write_text(
        "chromosome\tposition\tref\talt\tpval\n"
        "1\t1000\tA\tT\t0.01\n"
        "2\t2000\tC\tG\t0.23\n"
    )

    for i, v in enumerate(parsing.TabularParser(chroms, tsv_file, delimiter="\t")):
        if i == 0:
            assert v.chrom == "1"
            assert v.pos == 1000
            assert v.ref == "A"
            assert v.alt == "T"
            assert v.pval == 0.01

        if i == 1:
            assert v.chrom == "2"
            assert v.pos == 2000
            assert v.ref == "C"
            assert v.alt == "G"
            assert v.pval == 0.23

        if i > 1:
            raise AssertionError("Too many rows in test.tsv")


def test_incorrect_chrom(tmp_path: Path, chroms: pytest.fixture) -> None:
    """Test CSVParser with incorrect chromosome."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "chromosome,position,ref,alt,pval\n" "1,1000,A,T,0.01\n" "3,2000,C,G,0.23\n"
    )

    with pytest.raises(ValueError) as e:
        for _ in parsing.TabularParser(
            chroms, csv_file
        ):  # need to iterate through the generator to raise the error
            pass

    assert "Observed chromosome: 3 not in specified chromosomes" in str(e.value)


def test_incorrect_chrom_order(tmp_path: Path, chroms: pytest.fixture) -> None:
    """Test CSVParser with incorrect chromosome order."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "chromosome,position,ref,alt,pval\n" "2,1000,A,T,0.01\n" "1,2000,C,G,0.23\n"
    )

    with pytest.raises(ValueError) as e:
        for _ in parsing.TabularParser(chroms, csv_file):
            pass

    assert "Invalid chromosome order: 1 observed after 2" in str(e.value)


def test_incorrect_pos_order(tmp_path: Path, chroms: pytest.fixture) -> None:
    """Test CSVParser with incorrect position order."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "chromosome,position,ref,alt,pval\n" "1,1000,A,T,0.01\n" "1,999,C,G,0.23\n"
    )

    with pytest.raises(ValueError) as e:
        for _ in parsing.TabularParser(chroms, csv_file):
            pass

    assert "Invalid position order: 999 comes after 1000 on 1" in str(e.value)


def test_correct_pos_decrease_new_chrom_order(
    tmp_path: Path, chroms: pytest.fixture
) -> None:
    """Test CSVParser with correct position decrease and new chrom order."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "chromosome,position,ref,alt,pval\n" "1,1000,A,T,0.01\n" "2,999,C,G,0.23\n"
    )

    for i, v in enumerate(parsing.TabularParser(chroms, csv_file)):
        if i == 0:
            assert v.chrom == "1"
            assert v.pos == 1000
            assert v.ref == "A"
            assert v.alt == "T"
            assert v.pval == 0.01

        if i == 1:
            assert v.chrom == "2"
            assert v.pos == 999
            assert v.ref == "C"
            assert v.alt == "G"
            assert v.pval == 0.23

        if i > 1:
            raise AssertionError("Too many rows in test.csv")
