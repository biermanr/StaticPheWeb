"""Test the variant pydantic model."""

import pydantic
import pytest
from spheweb import variant


def test_good_variant_reqd_only() -> None:
    """Test the variant module."""
    data = {
        "chromosome": "1",
        "pos": 12345,
        "ref": "A",
        "alt": "T",
        "p_value": 0.001,
        "maf": 0.5,
        "beta": 0.5,
    }

    v = variant.Variant(**data)
    assert v.chrom == "1"
    assert v.pos == 12345
    assert v.ref == "A"
    assert v.alt == "T"
    assert v.pval == 0.001
    assert v.minor_allele_frequency == 0.5
    assert v.effect_size == 0.5


def test_good_variant_with_optionals() -> None:
    """Test the variant module."""
    data = {
        "chromosome": "1",
        "position": 12345,
        "ref_allele": "A",
        "alt_allele": "T",
        "pval": 0.001,
        "minor_allele_frequency": 0.5,
        "effect_size": 0.5,
        "alt_allele_freq": 0.5,
    }

    v = variant.Variant(**data)
    assert v.chrom == "1"
    assert v.pos == 12345
    assert v.ref == "A"
    assert v.alt == "T"
    assert v.pval == 0.001
    assert v.minor_allele_frequency == 0.5
    assert v.effect_size == 0.5
    assert v.alt_allele_freq == 0.5


@pytest.mark.parametrize(
    "reqd_field",
    [
        "chromosome",
        "position",
        "ref_allele",
        "alt_allele",
        "pval",
    ],
)  # type: ignore
def test_missing_required(reqd_field: str) -> None:
    """Missing required fields should fail."""
    data = {
        "chromosome": "1",
        "position": 12345,
        "ref_allele": "A",
        "alt_allele": "T",
        "pval": 0.001,
        "minor_allele_frequency": 0.5,
        "effect_size": 0.5,
    }

    del data[reqd_field]

    with pytest.raises(pydantic.ValidationError):
        variant.Variant(**data)


@pytest.mark.parametrize(
    "pval_field, pval_value",
    [
        ("pval", 1.001),
        ("p_value", -0.001),
        ("p_val", "str"),
    ],
)  # type: ignore
def test_bad_pval(pval_field: str, pval_value: float) -> None:
    """Bad pval should fail."""
    data = {
        "chromosome": "1",
        "position": 12345,
        "ref_allele": "A",
        "alt_allele": "T",
        pval_field: pval_value,
        "minor_allele_frequency": 0.5,
        "effect_size": 0.5,
        "alt_allele_freq": 0.5,
    }

    with pytest.raises(pydantic.ValidationError, match=pval_field):
        variant.Variant(**data)


@pytest.mark.parametrize(
    "maf_field, maf",
    [
        ("maf", -0.001),
        ("minor_allele_frequency", 0.501),
    ],
)  # type: ignore
def test_bad_maf(maf_field: str, maf: float) -> None:
    """Test bad minor-allele frequency."""
    data = {
        "chromosome": "1",
        "position": 12345,
        "ref_allele": "A",
        "alt_allele": "T",
        "pval": 0.001,
        maf_field: maf,
        "effect_size": 0.5,
        "alt_allele_freq": 0.5,
    }

    with pytest.raises(pydantic.ValidationError, match=maf_field):
        variant.Variant(**data)


def test_multiple_chromosome_fields() -> None:
    """If multiple chromosome validation aliases are provided, first in AliasChoices list is used."""
    data = {
        "chr": "2",
        "chrom": "1",
        "position": 12345,
        "ref_allele": "A",
        "alt_allele": "T",
        "pval": 0.001,
        "minor_allele_frequency": 0.5,
        "effect_size": 0.5,
        "alt_allele_freq": 0.5,
    }

    v = variant.Variant(**data)
    assert v.chrom == "1"
