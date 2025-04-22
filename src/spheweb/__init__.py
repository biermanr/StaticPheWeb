"""Static PheWeb website generator."""

from importlib import metadata

try:
    __version__ = metadata.version(__package__)
    del metadata  # optional, avoids polluting the results of dir(__package__)
except Exception:
    # When using `import src.spheweb` locally for debugging in jupyter notebook
    # I end up with python PackageNotFoundError
    __version__ = "beta"
