"""Tests for the package data."""

import importlib.resources

import pytest


def test_existing_html():
    """Test that the template html is present in the package-data."""
    p = importlib.resources.files("templates").joinpath("template.html")
    assert p.is_file()


@pytest.mark.xfail
def test_missing_html():
    """Test that the missing template is not present, should fail."""
    x = importlib.resources.files("templates").joinpath("missing_template.html")
    assert x.is_file()
