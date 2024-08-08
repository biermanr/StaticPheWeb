Aug 5th 2024: Static D3 Diagrams
---
Taking notes for myself directly in the github repo, not sure if this is a good idea.

I'm trying to figure out how to get a completely static d3 diagram
built from data, so first I tried to used `d3.csv()` to read in a local
.csv file but I was getting a CORS error in chrome which I guess
makes sense. I next tried to use `$.getJson()` on the local csv file,
but that also generated a CORS error.

Instead I'm thinking that I'll just have to hardcode the data into the
javascript file, which feels wrong but I think it will always work? I'll
use Jinja to insert the data into the javascript file so at least
its automated.

Oh, apparently there is a `.tojson()` jinja function that I can use to
convert the data to json, so I'll try that.

Aug 7th 2024: Adding HTML files as package-data
---
With help from Vineet, I was able to add the HTML files as package data.
I did this by creating a templates subdir of src/ and using the following
lines in the pyproject.toml file:
```toml
[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
templates = ["*.html"]
static = ["*.js"]
```

which worked and could be accessed with the following code:
```python
import importlib.resources
p = importlib.resources.files("templates", "template.html")
```

This is working with nox and pytest locally, but not on GHA. I think
this is because the package data is not being included in the wheel.
How can I test this locally?

I still don't know how to test it locally, but Vineet suggested that I
use this setup where I list the paths to the files in the package data:
```toml
[tool.setuptools.package-data]
spheweb = ["templates/*.html"]
```

this works locally with nox and pytest, so I'm going to try it on GHA.
This worked for GHA for python 3.10, 3.11, and 3.12, but not for 3.9.
Actually 3.9 fails on windows, mac, and ubuntu.
I get the error:
```
TypeError: expected str, bytes or os.PathLike object, not NoneType
```

on this line:
```python
p = importlib.resources.files("spheweb.templates").joinpath("missing_template.html")
```

I think this is because the `importlib.resources.files` function is not
returning a `pathlib.Path` object, but I'm not sure why. Maybe I need to
use a backport of importlib.resources? No, it's actually because it doesn't
handle the `joinpath` of NoneType. I've tried changing the code to:
```python
p = importlib.resources.files("spheweb.templates") / "missing_template.html"
```

I get the same error. The simplest fix is to just not do the "missing template" test.
Oh no, this somehow still failed with the same error, just on the actual template test.

```python
p = importlib.resources.files("spheweb.templates") / "template.html"
```

I can't figure out why this works locally but not on GHA. I think I'm just going
to drop python 3.9 from GHAs testing matrix. This seems so strange.
Well, at least GHA passes now.

Tomorrow I'll try to get some simple templating working with Jinja.
Also trying to get mypy working, currently running into errors with decorators
and "Cannot find implementation or library stub for module named 'click'".
Trying to run with `nox`.

Aug 8th 2024: Jinja Templating
---
Started by adding mypy to .pre-commit-config.yaml, excluding the
`cli.py` and `noxfile.py` files, which are complicated with external packages/decorators.

I'm trying to get Jinja templating working with the spheweb package.
I got this to work without too many issues.
I decided to use a jinja `FileSystemLoader` to load the templates from the package data
using `importlib.resources` and then render the template with the data.
```python
from jinja2 import Environment, FileSystemLoader
import importlib.resources

template_path = importlib.resources.files("spheweb").joinpath("templates")

env = Environment(loader=FileSystemLoader(template_path))
template = env.get_template("template.html")
rendered = template.render(data)
```

I think this should be a good approach that will be flexible, but I need to test on GHA.
The nox tests pass, including the one that I added to test the rendering.

Next I need to better understand how PheWeb is making the Manhattan plots.
I'm curious how many points are actually being plotted, since the plots load very quickly
and the MLMA files can be very large.
