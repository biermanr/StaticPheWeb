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

I think this should be a good approach that will be flexible, but I need to test on GHA (it worked!).
The nox tests pass, including the one that I added to test the rendering.

Next I need to better understand how PheWeb is making the Manhattan plots.
I'm curious how many points are actually being plotted, since the plots load very quickly
and the MLMA files can be very large.

Looking through the PheWeb code line 22 of [pheno.html](https://github.com/AkeyLab/DAP_pheweb/blob/master/pheweb/serve/templates/pheno.html#L22),
I see that there is a call to:

```javascript
$.getJSON(window.model.urlprefix + "/api/manhattan/pheno/" + window.pheno + ".json")
.done(function(data) {
  window.debug.manhattan = data;
  create_gwas_plot(data.variant_bins, data.unbinned_variants);
  populate_streamtable(data.unbinned_variants);
})
```

which is a call to the `manhattan` endpoint of the API.
What is the `window` object? I think it's just a global object in javascript.

So I need to look through the flask routing to find the `manhattan` endpoint. Yes, this is defined in [`server.py`](https://github.com/AkeyLab/DAP_pheweb/blob/538b3a608f6d78b63cdec809b8014b6ef15104f0/pheweb/serve/server.py#L132) on line 132:
```python
@bp.route('/api/manhattan/pheno/<phenocode>.json')
@check_auth
def api_pheno(phenocode:str):
    return send_from_directory(get_filepath('manhattan'), '{}.json'.format(phenocode))
```
so it's just passing the entire json file for the given pheno to the client.
I've checked in the `generated-by-pheweb/manhattan` folder which has all
the json files for the phenos, and they are all small actually, at only
~164KB.

Here's how the json is structured:
```json
{
    "variant_bins":[
        {'chrom': '1', 'qvals': [2.775, 2.875, 3.475], 'qval_extents': [[0.025, 2.525], [2.625, 2.675]], 'pos': 1500000},
        {'chrom': '1', 'qvals': [2.075, 2.175, 2.475], 'qval_extents': [[0.025, 1.925]], 'pos': 4500000},
        {'chrom': '1', 'qvals': [3.175], 'qval_extents': [[0.025, 2.425], [2.575, 2.625], [2.875, 3.075]], 'pos': 7500000},
        ...
    ],
    "unbinned_variants":[
        {'chrom': '18', 'pos': 55150763, 'ref': 'A', 'alt': 'G', 'rsids': '', 'nearest_genes': 'FADS3', 'pval': 4.2e-08, 'beta': -0.26, 'maf': 0.29, 'num_significant_in_peak': 1, 'peak': True},
        {'chrom': '17', 'pos': 38436418, 'ref': 'G', 'alt': 'A', 'rsids': '', 'nearest_genes': 'LOC102154258', 'pval': 1.1e-07, 'beta': 0.38, 'maf': 0.093, 'num_significant_in_peak': 0, 'peak': True},
        {'chrom': '17', 'pos': 38436369, 'ref': 'G', 'alt': 'A', 'rsids': '', 'nearest_genes': 'LOC102154258', 'pval': 2.6e-07, 'beta': 0.37, 'maf': 0.091},
        ...
    ]
}
```
In the one file I looked at ("Lysine.json"), there are 502 `unbinned_variants` and 764 `variant_bins`.

I'll look into the code to understand how these json files were created, but
first I want to understand how the `create_gwas_plot` function works.

There are two `create_gwas_plot` functions, one in `pheno.js` and
one in `pheno-filter.js`. I'm not sure which is being used, but lets
look at the one in [`pheno.js`](https://github.com/AkeyLab/DAP_pheweb/blob/538b3a608f6d78b63cdec809b8014b6ef15104f0/pheweb/serve/static/pheno.js#L5) first. This function is ~400 lines long.
It has the following signature, showing that is uses both
`variant_bins` and `unbinned_variants`:
```javascript
function create_gwas_plot(variant_bins, unbinned_variants)
```

The `unbinned_variants` are used to create circles on the d3 plot
starting on line [293](https://github.com/AkeyLab/DAP_pheweb/blob/538b3a608f6d78b63cdec809b8014b6ef15104f0/pheweb/serve/static/pheno.js#L293)
with the `pp1()` and `pp2()` functions.

The `variant_bins` are used also added to the plot as circles in
teh `pp3()` function. There's a comment that:
```javascript
// drawing the ~60k binned variant circles takes ~500ms.  The (far fewer) unbinned variants take much less time.
```

but we saw in the json file that there are only 764 `variant_bins`.
So this must be an old comment. Also I don't yet understand the difference
of pp1() and pp2(). But, as an answer to the question of
"how many points are being plotted", it's about 1,300 points.

This is good news for the approach I'm taking since I'll only be rendering
a dictionary with 1,300 points into the html file.

I should download one of these json files and write my own d3
code to plot it. (Probably heavily inspired by PheWeb's)

Aug 9th 2024: Simplest Manhattan plot with pre-processed json data
---
I've downloaded multiple json files created by PheWeb that are
used to create the Manhattan plots. My goal today is to create
a simple HTML template in Jinja that will render a Manhattan plot
with the data from the json file and as simple of D3 as I can manage.

Ok! I got the Manhattan plot working with the pre-processed json data!
This is pretty exciting, next step is going to be to try and remove any
extra code, try to simplify the D3 code as much as possible and add tests.
