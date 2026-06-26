"""Static PheWeb website generator."""

from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except Exception:
    # When using `import src.spheweb` locally for debugging in jupyter notebook
    # I end up with python PackageNotFoundError, this is a workaround
    __version__ = "beta"
finally:
    del metadata  # optional, avoids polluting the results of dir(__package__)
