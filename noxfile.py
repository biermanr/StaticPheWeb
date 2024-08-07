"""noxfile.py to test locally."""

import nox


# python="3.10" is failing with "RuntimeError: failed to find interpreter for Builtin discover of python_spec='python3.10'"
@nox.session(python=["3.9", "3.11", "3.12"])
def tests(session):
    """Test install and pytest."""
    session.install(".", "pytest-cov", "pytest")
    session.run("pytest", "--cov")
