"""Configuration for pytest."""

import pytest


def pytest_addoption(parser):  # type: ignore
    """Create a command line option to run slow tests."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):  # type: ignore
    """Skip slow tests if --run-slow is not provided."""
    if config.getoption("--run-slow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
