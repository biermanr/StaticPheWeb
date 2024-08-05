"""Process input data to fill in HTML and JS templates."""

import importlib.resources

# example of how to access a package resource
f = importlib.resources.files("spheweb.templates").joinpath("template.html")
print(f)
