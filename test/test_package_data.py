"""Tests for the package data."""

import importlib.resources


def test_existing_html():
    """Test that the template html is present in the package-data."""
    p = importlib.resources.files("spheweb.templates").joinpath("template.html")
    assert p.is_file()


def test_missing_html():
    """Test that the missing template is not present, should fail."""
    p = importlib.resources.files("spheweb.templates").joinpath("missing_template.html")
    assert not p.is_file()
