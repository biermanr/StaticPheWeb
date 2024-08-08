"""Tests for spheweb CLI."""

from click.testing import CliRunner
from spheweb import __version__
from spheweb.cli import spheweb

runner = CliRunner()


def test_version():
    """Test the version command."""
    result = runner.invoke(spheweb, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"spheweb, version {__version__}\n"


def test_parse_help():
    """Test the help message for the parse command."""
    result = runner.invoke(spheweb, ["build", "--help"])
    assert result.exit_code == 0
