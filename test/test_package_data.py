"""Tests for the package data."""

import importlib.resources


def test_existing_html():
    """Test that the template html is present in the package-data."""
    p = importlib.resources.files("spheweb.templates") / "template.html"
    assert p.is_file()
