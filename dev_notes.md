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
What is pp1() vs. pp2() vs. pp3() etc?

When I commented out pp2(), it removed the most significant points from the plot.
Ok, apparently pp1() is for "variant_hover_rings"(?) which have opacity of 0
meaning that they are invisible. pp2() is for "variant_points" which are the actual
dots in the plot. Removing pp1() doesn't seem to have any ill-effects.

Getting rid of pp3() removes the low p-value points from the plot.

I've renamed pp2() to `add_variant_points()` and pp3() to `add_variant_bins()`.

Ok, now how am I going to test this? I could parse the resulting HTML file
to ensure that it's valid HTML at the very least. I think SELENIUM testing
is overkill for this project, but I could use it to test the interactivity of the plot.

Ok, I added this and it passes, but again it's not testing the javascript, just the HTML.

Now I'm going to switch gears and figure out how the json file is created by
PheWeb from the input CSV data. This is done in the `manhattan.py` file here:
`https://github.com/AkeyLab/DAP_pheweb/blob/master/pheweb/load/manhattan.py`
and it's only ~200 lines long.

Seems like the crux of the code is:
```python
def make_manhattan_json_file_explicit(in_filepath:str, out_filepath:str) -> None:
    binner = Binner()
    with VariantFileReader(in_filepath) as variants:
        for variant in variants:
            binner.process_variant(variant)
    data = binner.get_result()
    write_json(filepath=out_filepath, data=data)
```

where Binner is a class created in this file that has a `process_variant` method.

The `for` loop is processing each variant in the input CSV file withe the Binner,
which is handling the logic of identifying peaks in the data. This is documented
very nicely in the function docstring:

```python
def process_variant(self, variant:Variant) -> None:
    '''
    There are 3 types of variants:
        a) If the variant starts or extends a peak and has a stronger pval than the current `peak_best_variant`:
            1) push the old `peak_best_variant` into `unbinned_variant_pq`.
            2) make the current variant the new `peak_best_variant`.
        b) If the variant ends a peak, push `peak_best_variant` into `peak_pq` and push the current variant into `unbinned_variant_pq`.
        c) Otherwise, just push the variant into `unbinned_variant_pq`.
    Whenever `peak_pq` exceeds the size `conf.get_manhattan_peak_max_count()`, push its member with the weakest pval into `unbinned_variant_pq`.
    Whenever `unbinned_variant_pq` exceeds the size `conf.get_manhattan_num_unbinned()`, bin its member with the weakest pval.
    So, at the end, we'll have `peak_pq`, `unbinned_variant_pq`, and `bins`.
    '''
```

So, this answers my question of what the `variant_bins` and `unbinned_variants` are in the json file.
The `variant_bins` are the peaks in the data, and the `unbinned_variants` are the "combined" variants that are not in a peak.
Basically, "standout" vs. "normal" variants. I think there might be a simpler way to do this where you just bin all the variants
by a static window-size and only display the most significant variant per-window in the plot. The human
genome is 3.2 billion base pairs long, so if we bin by 1 million base pairs, we'd have 3,200 bins. Hmm, maybe this is
not as good as the current method. Oh wait, they use a `BIN_LENGTH` of 3e6, so ~1,000 bins for the human genome.
Maybe the simpler approach I'm thinking about will be fine afterall.

Some of the MLMA files has 11 million variants, so these are getting boiled down to ~800 bins + 500 variants by current PheWeb.
For dog weight phenotype, there are only 42 bins for chr1, 29 for chr2, 31 for chr3.
Maybe I'll create an abstract base class for the Binner and then create a new class that just bins by a static window-size.
Then if that looks bad I can create a new Binner that bins by peaks, or some other method.

Ok, I started adding this, but I'm making a lot of architectural decisions all at once, so I'm going to hold off for now.
Instead I'm going to try to think of what the user interface for this tool will look like.

Let's say the user runs the following command:
```bash
spheweb build \
    --gtf genes.gtf \
    --chroms chroms.txt \
    --phenos pheno-list.json \
```

Where `genes.gtf` is a GTF file with the gene annotations and `pheno-list.json` is a json file with the list of per-phenotype MLMA/CSV files.
The `chroms.txt` file is just a text file with a column for chromosome names, start, and end positions, like:
```
chr1 1 248956422
chr2 1 242193529
...
```

We can have some default `--chroms` like how plink does it with `--chroms hg19` or `--chroms hg38` or `--chroms canFam4` etc.
spheweb should also accept gff3 files since those are supposed to be the new standard for gene annotations.
Finally, maybe we could provide the option to download the gene annotations and chromosomes from UCSC, but having users
download a gtf file themselves sounds like a good place to start.

We can have `pheno-list.json` be the same structure as PheWeb currently uses, something like:
```json
{
    "phenos": [
        {
            "name": "Dog Weight",
            "file": "dog_weight.csv"
        },
        {
            "name": "Dog Height",
            "file": "dog_height.csv"
        }
    ]
}
```
This file might not be the easiest format for people to use, but it's a good place to start since PheWeb already demands it.
Maybe there can be a separate spheweb command eventually that will take a directory of MLMA files and create this `pheno-list.json` file.
We can have some other configuration parameters eventually, but not at the start.


Aug 12th 2024: Data validation
---

I started today thinking I would copy the PheWeb binning code for manhattan plots, so I was reading through the `manhattan.py` file
and I saw that they do a good job of validating the input data CSV/TSV which I hadn't considered.

I like how simple their validating/parsing/binning code looks:
```python
def make_manhattan_json_file_explicit(in_filepath:str, out_filepath:str) -> None:
    binner = Binner()
    with VariantFileReader(in_filepath) as variants:
        for variant in variants:
            binner.process_variant(variant)
    data = binner.get_result()
    write_json(filepath=out_filepath, data=data)
```

I want to copy this idea where there is a `Parsing` abstract base class that is
responsible for validating the input data from a few different common formats.
Then the `Binning` classes will make use of the `Parsing` classes to get the data.
I'm thinking that the `Parsing` class will be iterable and will yield the validated
data row-by-row. This way the `Binning` classes can be more flexible in how they
process the data. All the different `Parsing` classes will need to provide the same
interface, which I can do by having a `Variant` dataclass that all the `Parsing` classes
will return.

I'll start with creating the `Variant` pydantic class and test that
with different inputs. So far I'm pleased with how this is going, its
been really easy and expressive to define:
* Optional fields
* Multiple aliases for the same field
* Bounds on numeric fields

I've written multiple tests for validating a test variant dictionary
including tests that use `pytest.raises` to ensure certain inputs fail.
The error messages are currently very ugly, but I'll fix that later.

Ok, I think I've got the `Variant` class working well, so I'm going to
move on to the `Parsing` classes. I'm going to start with the `CSVParser`
which will use the `csv` module to read in the data and validate it.
