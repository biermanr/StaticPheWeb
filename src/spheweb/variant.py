"""pydantic model for a variant/SNP."""

import typing

from pydantic import AliasChoices, BaseModel, Field

# NOTE TODO Define the valid chromosomes dynamically from config
CHROMS = typing.Literal[
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "X",
    "Y",
    "MT",
]


class Variant(BaseModel):  # type: ignore
    """pydantic model for a variant/SNP."""

    chromosome: typing.Literal[CHROMS] = Field(
        validation_alias=AliasChoices(
            "chromosome", "chrom", "chr", "#chrom", "#chromosome", "#chr"
        )
    )
    position: int = Field(ge=0, validation_alias=AliasChoices("position", "pos"))
    ref_allele: str = Field(
        min_length=1, max_length=1, validation_alias=AliasChoices("ref_allele", "ref")
    )
    alt_allele: str = Field(
        min_length=1, max_length=1, validation_alias=AliasChoices("alt_allele", "alt")
    )
    p_value: float = Field(
        ge=0, le=1, validation_alias=AliasChoices("p_value", "pval", "p_val")
    )
    minor_allele_frequency: typing.Optional[float] = Field(
        default=None,
        ge=0,
        le=0.5,
        validation_alias=AliasChoices("minor_allele_frequency", "maf"),
    )
    alt_allele_freq: typing.Optional[float] = Field(
        default=None,
        ge=0,
        le=1.0,
        validation_alias=AliasChoices("alt_allele_freq", "alt_freq"),
    )
    effect_size: typing.Optional[float] = Field(
        default=None, validation_alias=AliasChoices("effect_size", "beta")
    )
