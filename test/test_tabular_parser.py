"""Test CSV parser."""

from pathlib import Path

from spheweb import parsing


def test_good_csv_parse(tmp_path: Path) -> None:
    """Test CSVParser."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "chromosome,position,ref,alt,pval\n" "1,1000,A,T,0.01\n" "2,2000,C,G,0.23\n"
    )

    for i, v in enumerate(parsing.TabularParser(csv_file)):  # type: ignore
        if i == 0:
            assert v.chromosome == "1"
            assert v.position == 1000
            assert v.ref_allele == "A"
            assert v.alt_allele == "T"
            assert v.p_value == 0.01

        if i == 1:
            assert v.chromosome == "2"
            assert v.position == 2000
            assert v.ref_allele == "C"
            assert v.alt_allele == "G"
            assert v.p_value == 0.23

        if i > 1:
            raise AssertionError("Too many rows in test.csv")


def test_good_tsv_parse(tmp_path: Path) -> None:
    """Test CSVParser with a TSV."""
    tsv_file = tmp_path / "test.tsv"
    tsv_file.write_text(
        "chromosome\tposition\tref\talt\tpval\n"
        "1\t1000\tA\tT\t0.01\n"
        "2\t2000\tC\tG\t0.23\n"
    )

    for i, v in enumerate(parsing.TabularParser(tsv_file, delimiter="\t")):  # type: ignore
        if i == 0:
            assert v.chromosome == "1"
            assert v.position == 1000
            assert v.ref_allele == "A"
            assert v.alt_allele == "T"
            assert v.p_value == 0.01

        if i == 1:
            assert v.chromosome == "2"
            assert v.position == 2000
            assert v.ref_allele == "C"
            assert v.alt_allele == "G"
            assert v.p_value == 0.23

        if i > 1:
            raise AssertionError("Too many rows in test.tsv")
