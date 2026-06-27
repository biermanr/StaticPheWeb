"""pydantic model for a variant/SNP."""

from pydantic import AliasChoices, BaseModel, Field


class Variant(BaseModel):
    """pydantic model for a variant/SNP."""

    chrom: str = Field(
        validation_alias=AliasChoices(
            "chromosome", "chrom", "chr", "#chrom", "#chromosome", "#chr"
        )
    )
    pos: int = Field(ge=0, validation_alias=AliasChoices("position", "pos"))
    ref: str = Field(
        min_length=1, max_length=1, validation_alias=AliasChoices("ref_allele", "ref")
    )
    alt: str = Field(
        min_length=1, max_length=1, validation_alias=AliasChoices("alt_allele", "alt")
    )
    pval: float = Field(
        ge=0, le=1, validation_alias=AliasChoices("pval", "p_value", "p_val")
    )
    maf: float | None = Field(
        default=None,
        ge=0,
        le=0.5,
        validation_alias=AliasChoices("minor_allele_frequency", "maf"),
    )
    alt_allele_freq: float | None = Field(
        default=None,
        ge=0,
        le=1.0,
        validation_alias=AliasChoices("alt_allele_freq", "alt_freq"),
    )
    effect_size: float | None = Field(
        default=None, validation_alias=AliasChoices("effect_size", "beta")
    )
