"""Tests for the package data."""

import importlib.resources


def test_missing_html() -> None:
    """Test that the missing template is not present, should fail."""
    p = importlib.resources.files("spheweb.templates").joinpath("missing_template.html")
    assert not p.is_file()
