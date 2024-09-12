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

I moved on to writing a CSV parser, and WOW I was not expecting how nice
the code would look:
```python
class CSVParser(Parser):
    """Parser for CSV/TSV files."""
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def __iter__(self) -> Iterable[variant.Variant]:
        """Parse the input CSV file and return a generator of Variant."""
        with open(self.file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                yield variant.Variant(**row)
```

I wrote a test, with the help of github copilot that:
1. Writes a mock CSV file with two lines of data
2. Creates a `CSVParser` object with the mock file
3. Iterates over the `CSVParser` object and checks that the data is correct

This works so well, and it seems so simple!
I ended up renaming `CSVParser` to `TabularParser` since it can handle both CSV and TSV files, etc. Added an additional test for TSV.

pydantic is really nice for this use case, and having github copilot
help write tests is really nice.


Aug 13th 2024: Implementing the Binner
---

Yesterday I got the `Variant` and `TabularParser` classes working, so today I'm going to implement a `Binner` class.

The `Binner` from PheWeb is kind of complicated,
so it might take me a while to implement it in a
way that I understand and I'm happy with, but it
will be nice to have the compatibility with PheWeb
and know what output I should be getting.

Maybe before doing this though, I'm a little nervous
that the `TabularParser` is slow for the large MLMA files, so I'm going to test how long it takes to
just parse one of the DAP MLMA files, maybe weight.
This file is ~500 MB in size with 9.8M lines.

I added a click subcommand `validate_input` which just creates a tabular parser, and iterates through
the lines, counting how many there are:

```python
@spheweb.command()
@click.argument("tabular_file", type = Path)
@click.option("--delim", "-d", default=',', type = str)
def validate_input(tabular_file, delim) -> None:
    """Validate format of input CSV file, or use --delim to specify other tabular format."""
    num_lines = sum(1 for _ in parsing.TabularParser(tabular_file, delim))
    click.echo(f"File {tabular_file} with {num_lines} successfully parsed!")
```

It "only" took 25 seconds to get through this file,
so it's not terribly unworkably slow for now,
but I'm certain it could be a lot faster. Iterating
over the lines with just a `with open()` and not
validating the input only takes 1 second.

If someone had 300 phenotypes they wanted to use
for the PheWeb, it would take 150 minutes or around
2 hours, and this is just for parsing the input.

How long does it take if I use the `csv.DictReader`
but not the `pydantic` model for validation? 9 seconds, ok. So the `csv.DictReader` is slow, but
so is the pydantic model parsing. I'll put this
on the backburner for now and try to get something
working all the way through first.

#### Understanding the Binner
Ok, now I'm going to read through the PheWeb binning
code more closely and take notes. It inits the
`Binner` with two `MaxPriorityQueue` objects that
PheWeb defined itself. The goal of these queue's is
to be a maximum size heap that maintains heap order.

The function `process_variant` is called for each
variant in the input data. It has some logic to
try and figure out how many bins to create, but I
think it's flawed since it can be set and unset
by subsequent variants in the list, so the order
of variants will effect the final number of bins.

```python
if variant['pval'] != 0:
    qval = -math.log10(variant['pval'])
    if qval > 40:
        self._qval_bin_size = 0.2 # this makes 200 bins for a y-axis extending past 40 (but folded so that the lower half is 0-20)
    elif qval > 20:
        self._qval_bin_size = 0.1 # this makes 200-400 bins for a y-axis extending up to 20-40.
```

Next, if a variant is in a peak because it has
a sufficiently low p-value, it will be added to
an existing peak or a new peak will be created.

```python
if variant['pval'] < conf.get_manhattan_peak_pval_threshold(): # part of a peak
    if self._peak_best_variant is None: # open a new peak
        ...

    elif self._peak_last_chrpos[0] == variant['chrom'] and self._peak_last_chrpos[1] + conf.get_manhattan_peak_sprawl_dist() > variant['pos']: # extend current peak
        ...

    else: # new chromosome or far enough away, close old peak and open new peak
        ...
```

So it seems like it's looking one sorted variant
at a time and deciding where to put the variant.

There are two helper functions for actually pushing onto the peak and bin priority queues.

```python
    def _maybe_peak_variant(self, variant:Variant) -> None:
        self._peak_pq.add_and_keep_size(variant, variant['pval'],
                                        size=conf.get_manhattan_peak_max_count(),
                                        popped_callback=self._maybe_bin_variant)

    def _maybe_bin_variant(self, variant:Variant) -> None:
        self._unbinned_variant_pq.add_and_keep_size(variant, variant['pval'],
                                                    size=conf.get_manhattan_num_unbinned(),
                                                    popped_callback=self._bin_variant)
```

So the `Binner` is maintaining two priority queues, one for the peaks and one for the unbinned variants. Each entry in the priority queue is a single `Variant` object that is used as the
representative of the peak or bin.

The `popped_callback` is a function that gets called for variants that are removed from
the peak priority queue, to see if it should be added to the bin pq, and then finally to
the _bin_variant function which actually bins the variant.

I don't know why this code feels so complicated, I still don't have a great understanding
of what it's trying to accomplish. Which Variants should be Peaks, and which should be Bins?

I see there is a `conf.py` file which specifies a maximum of 500 peaks and 500 bins.
And there is a "sprawl distance" of 200_000 which is used to determine the maximum distance
between two significant variants to be considered part of the same peak.

Ok, maybe this is as far as I go into understanding the code, and I'm just going to implement
it as is and make sure I can get the same output as PheWeb.

Update on this. I was able to get the legacy
code working, linted, mypy'd, and tested.
It ran without error, but produced a
different JSON output on the same input data.
Oh, I should also say I was able to get a manhattan d3 plot
working after I adjusted the `Variant` pydantic class to have
the same field names as the PheWeb `Variant` dict.

I will have to return to this, I want to know why there are
differences when I copied/pasted their code and made what I thought
were only refactorings.

I also learned a lot about Iterable vs. Iterator (mypy wants the later)
and I made some more organization decisions about the project structure.
Right now, for example, Binner's must use a parser as an argument to
their `bin` function.

Aug 14th 2024: Continued work on Binner
---
I thought I'd check to make sure that the json file I copied
from a previous PheWeb run was the same as if I generate it again
using the DAP pheweb, so I ran `pheweb process` on just the weight
CSV file. This was also helpful in seeing that the `parse-input-files`
step took 88 seconds for the single phenotype, so the 30 seconds I'm
seeing (so far at least) isn't too bad.

```bash
==> Starting `pheweb parse-input-files`
Processing 1 phenos
Completed    1 tasks in 87 seconds
==> Completed in 88 seconds
```

Oh wait, this parse-input-files step actually just
takes the input CSV, parses it, and generates and output
gzipped CSV in `generated-by-pheweb/parsed/Weight`

I saw that this file is 9,867,132 lines long, so it's
just a pre-processing step that I'm pretty sure we don't
need to copy. There is a lot of logic in the
`pheweb/load/read_input_file.py` script which is already
handled for us by pydantic, except we need to add ordering
checks to make sure the chromosomes and positions are in order.

I'll add these checks now before I forget.
My idea is to make the `Parser` class accept
a `ChromList` object.

I'm actually having trouble figuring out
how to add the order-validation logic
into the parser. I want to ensure that
when someone writes a new parser, they
don't forget to validate the order. So
I don't want to just add this logic to
the __iter__ method of the TabularParser.

Maybe I should be using a normal class
for Parser instead of an abstract base
class, so that way I can implement the
`__iter__` method in the base class and
have it call a `validate_order` method
that will also be implemented in the base
class.

This is the implementation I decided on, but I think
it's not very clean because there's a lot of validation
logic for chroms/positions in the `Parser` base class
that would make more sense to move to the `Variant` pydantic class.

Ok, well that was a long aside in order to implement checks for
the data being in order. Let's see how much those checks slow
down the parsing with a call to `spheweb validate-input`. Oh,
very nice, it's still 28 seconds!

Returning to trying to figure out why the JSON produced by PheWeb
and Spheweb are different. I think there might be additional processing
occuring in the steps before the manhattan processing step. Here are the
steps in order (there are a lot of steps):
1. `pheweb phenolist verify`
    * Took 0 seconds, just checks that the phenolist is valid
2. `pheweb parse-input-files`
    * Took 88 seconds to convert the input CSV into a parsed GZIP with the same number of rows
3. `pheweb sites`
    * Took 39 seconds. This extracts all variants from all phenotypes and unions them. Writing out to `sites/sites-unannotated.tsv`
4. `pheweb make-gene-aliases-sqlite3`
    * Took 51 seconds. This "Makes a database of all gene names and their aliases for easy searching."
5. `pheweb add-rsids`
    * Took 39 seconds. This annotates the sites with RSIDs. Writing out to `sites/sites-rsids.tsv`
6. `pheweb add-genes`
    * Took 71 seconds. Annotates the sites with the nearest genes. Writes out to `sites/sites.tsv`
7. `pheweb make-cpras-rsids-sqlite3`
    * Took 32 seconds. Makes a database to convert between RSIDs and chrom/pos/ref/alt (CPRA).
8. `pheweb augment-phenos`
    * Took 87 seconds. I think this is attributing the variants to the phenotypes. Produces the `generated-by-pheweb/pheno_gz/*.gz` files and associated tabix files.
9. `pheweb matrix`
    * Took 12 seconds. This "creates a single large tabix file with all the variants for all phenotypes." Produces `generated-by-pheweb/matrix.tsv.gz` and associated tabix file.
10. `pheweb gather-pvalues-for-each-gene`
    * Took 10 seconds. This gets the best p-values for each gene and writes out `generated-by-pheweb/best-phenos-by-gene.sqlite3`.
11. `pheweb manhattan`
    * Took 42 seconds and produced the `generated-by-pheweb/manhattan/Weight.json` file.
    * Takes as input the `pheno_gz/` files.


I reran all these steps and still got a disagreement for the JSON file between
PheWeb and SpheWeb. They both have 764 `variant_bins`, although the binning
is different, but additionally the `unbinned_variants` are different with
PheWeb having 596 unbinned_variants and Spheweb having 1000 unbinned_variants.


Aug 22nd 2024: Continued Binner Tracing
---
Returning to this project after a break. Immediate todo is still to figure out why the
`unbinned_variants` are different between PheWeb and Spheweb.

I'm going to edit the steps list above with my understanding of what each step is doing.

I think the `sites` step might be doing some filtering as it extracts all variants from all phenotypes and unions them.
It uses the `VariantFileReader` in `file_utils` to read in the variants from the input
CSV files. Spheweb doesn't use this because it reads in the variants directly from the input CSV file with the `TabularParser`.
It looks like, no, there isn't any filtering going on here. The `class _vfr_only_per_variant_fields` is what's being used. I'll check the output of this
step to verify. Ok, this file is gzipped, but has `9,867,132` lines, including the header line, which is the same as the original input, so no filtering is happening here.

The `make_gene_aliases_sqlite3` step is creating a sqlite3 database of all gene names and their aliases for easy searching, I don't think this has anything to do with
filtering the variants. The output of this step is `resources/gene_aliases-v{}.sqlite3`.

Next is the `add-rsids` step which is annotating the sites with RSIDs. This produces the output file `sites/sites-rsids.tsv` which is also `9,867,132` lines long, so again no filtering is being done here.

Next is the `add-genes` step which annotates with the closest gene. This produces the output file `sites/sites.tsv` which is also `9,867,132` lines long, so again no filtering is being done here.

Next is the `augment_phenos` step which looks like it assigns each phenotype sites
from the combined sites file. Since we're just running on weights, it just produces the `generated-by-pheweb/pheno_gz/Weight.gz` file and a corresponding tabix index. This file has `9,867,132` lines, so no filtering is being done here.

Next is the `matrix` step which combines all the phenotypes into a single large tabix file. This produces the `generated-by-pheweb/matrix.tsv.gz` file which is also `9,867,132` lines long, so no filtering is being done here.

Next is the `gather-pvalues-for-each-gene` step which gets the best p-values for each gene. This produces the `generated-by-pheweb/best-phenos-by-gene.sqlite3` file. And I don't think this has anything to do with the number of sites or filtering.

Finally is the `manhattan` step which produces the `generated-by-pheweb/manhattan/Weight.json` file which is the one I'm comparing to the Spheweb output. This uses the
`pheno_gz` gzipped tsv file `generated-by-pheweb/pheno_gz/Weight.gz` to produce
the manhattan plot json file. It looks like I've pretty much copied all the logic
from this step, so I'm not sure why the output is different.

Maybe I'll try using the `pheno_gz` file from PheWeb for spheweb to see if that changes the output. Here's a quick comparison of the heads of these two files:

```bash
==>    dd_weight_lbs_N-7378.loco.csv  <==
chrom  pos                            ref  alt  pval      beta           maf
1      5753                           G    A    0.622122  0.00430721     0.42477600000000004
1      13961                          G    T    0.622616  0.0141087      0.0194497
1      14118                          G    C    0.721309  0.00951598     0.0242613
1      14132                          A    C    0.999789  5.68787e-06    0.0385606
1      14926                          C    T    0.786221  -0.00919041    0.0138927
1      14935                          A    T    0.2782    -0.0391365     0.0119951
1      14990                          G    A    0.125876  0.0279618      0.0508946
1      15016                          G    A    0.637314  -0.00600085    0.120968
1      15091                          A    T    0.981062  0.000608517    0.0238547

==>    weight_pheno_gz.tsv            <==
chrom  pos                            ref  alt  rsids     nearest_genes  pval       beta        maf
1      5753                           G    A                   ENPP1     0.62       0.0043      0.42
1      13961                          G    T                   ENPP1     0.62       0.014       0.019
1      14118                          G    C                   ENPP1     0.72       0.0095      0.024
1      14132                          A    C                   ENPP1     1.0        5.7e-06     0.039
1      14926                          C    T                   ENPP1     0.79       -0.0092     0.014
1      14935                          A    T                   ENPP1     0.28       -0.039      0.012
1      14990                          G    A                   ENPP1     0.13       0.028       0.051
1      15016                          G    A                   ENPP1     0.64       -0.006      0.12
1      15091                          A    T                   ENPP1     0.98       0.00061     0.024
```

You can see that the `pheno_gz` (2nd file) has two additional columns,
`rsids` and `nearest_genes`, but the rest of the columns are the same.
Additionally the `pheno_gz` is rounding the values of `pval`, `beta`, and `maf`.

I reran the `generate_legacy_manhattan_json` function with the `pheno_gz` file
and got the same number of `unbinned_variants` as spheweb (1000) if its run
directly on the CSV file. So now I'm convinced that the difference is due to
the legacy_binning that I tried to implement.

This was kind of a frustrating exercise, but also a good learning experience and
another opportunity to walk through PheWeb's codebase.

I've decided that I'm going to allow `variant` to just be a dict so that I can
use all the logic and fields from the PheWeb binning, rather than using my new
pydantic model. I had a few lines of code commented out that I didn't think was
doing anything, but I was probably wrong(?). I'm rerunning with this change. Nope,
still have 1000 unbinned_variants, instead of 596.

Well I think I'm going to have to give up on this for now. Visually the plots
look the same, so I'm not sure what the difference is. Next I'll implement the
datatable below the plot and see if those differ.

Adding the javascript datable under the plot
----

It looks like the StreamTable is created in the `pheno.html` template file by
creating a `<table>` element with the id `stream_table`. There is an import
for a local copy of the `pheweb/serve/static/vendor/stream_table-1.1.1.min.js`
file.

Also there is a call to `populate_streamtable(data.unbinned_variants);` in the
`pheno.html` template. This function is defined in `pheweb/serve/static/pheno.js`.
Note how it is only called with the `unbinned_variants` data.

I think I'm instead just going to use Jinja templating to build the table without
the use of the `stream_table` library. This won't have pagination, but I think it's
an easy place to start and I can always add it later.

I've made the table, it was really easy with jinja!
Just added:
```html
<div id="variants_table_container">
    <table id="stream_table" class="table table-striped table-bordered">
    <thead>
        <tr>
        <th>Variant</th>
        <th>Nearest Gene(s)</th>
        <th>MAF</th>
        <th>P-value</th>
        <th>Effect Size (se)</th>
        </tr>
    </thead>
    <tbody>
    {% for v in data["unbinned_variants"] %}
    <TR>
        <TD>{{ '{}:{} {}/{}'.format(v["chrom"], v["pos"], v["ref"], v["alt"]) }}</TD>
        <TD>No genes</TD>
        <TD>{{ '{:.2e}'.format(v["minor_allele_frequency"]) }}</TD>
        <TD>{{ '{:.2e}'.format(v["pval"]) }}</TD>
        <TD>{{ '{:.2e}'.format(v["effect_size"]) }}</TD>
    </TR>
    {% endfor %}
    </tbody>
    </table>
</div>
```

And this made an ugly table, but it's a start and looks like:
```
Variant	Nearest Gene(s)	MAF	P-value	Effect Size (se)
15:41521885 T/C	No genes	4.82e-01	9.03e-50	-1.48e-01
15:41521682 A/G	No genes	4.82e-01	1.11e-49	-1.48e-01
```

Actually, it looks like these two peaks are too close together, they are only 203 base pairs apart, which is closer than the 200,000 base pair sprawl distance. Looking at the PheWeb results, I only see the first peak, not the second. Ahah! This is a good way
to debug.

Also I'm happy to say that the .html file is only 500K, so it's still small enough to be reasonable to load in the browser really quickly.

Ahah! I definitely found a bug with how the `self.manhattan_peak_sprawl_dist` was
being used by me. I had incorrectly substituted some code to avoid a function call.
This might work now.

No, there is still an issue with these two peaks both being recorded in the output.
Need to follow-up on another day.


Sept 3rd 2024: Continued debugging of legacy binning
---
Noticing another discrepancy between the PheWeb and Spheweb output where
the 0-th "variant bin" for the PheWeb output is:
```python
{'chrom': '1',
 'qvals': [3.05, 3.65, 3.95],
 'qval_extents': [[0.05, 2.85], [3.35, 3.45]],
 'pos': 1500000}
```

whereas the Spheweb output is
```python
{'chrom': '1',
 'qvals': [3.05, 3.95],
 'qval_extents': [[0.05, 2.85], [3.35, 3.45], [3.65, 3.75]],
 'pos': 1500000}
```

so it seems like the Spheweb output is missing the 3.65 from `qvals` and somehow
added it to the `qval_extents`.

I'm rerunning PheWeb to regenerate the output to see if the bug is still present,
it probably should be since I haven't changed anything in the code, but this is
just a sanity check. The 11 steps of `pheweb process` need to finish. Will probably
take around 10 minutes.

I should restrict to just chr10 and rerun both PheWeb and SpheWeb after this to
get a smaller output to compare.

The outputs are really similar on just chr10, but there are still some differences.
Looks like the `qval_extents` are still different:
```python
#pheweb chr10 variant_bins
{'chrom': '10',
 'qvals': [6.45, 6.65],
 'qval_extents': [[0.05, 4.75], [5.05, 6.25], [6.85, 7.85]],
 'pos': 1500000}
```


```python
#spheweb chr10 variant_bins
{'chrom': '10',
 'qvals': [6.45, 6.65],
 'qval_extents': [[0.05, 4.85], [5.05, 6.25], [6.85, 7.85]],
 'pos': 1500000}
```

I think there must be differences in the `_get_qvals_and_qval_extents` function.
No, the code looks identical. I'm going to try debugging with pdb. Ok, using pdb
was helpful for spheweb, I understand now that the `qval` and `qval_extents` are
calculated at the end in the `get_result` function which is called once after all
the variants have been processed. The difference between `qval` and `qval_extents` is
that `qvals` are the "singular" q-values that can occur when trying to bin the q-values.
For example, walking through the `for` loop binning the qvalues in the `_get_qvals_and_qval_extents`, this populates the `extents` list to look like:
```python
[(0.05, 4.85), (5.05, 6.25), (6.45, 6.45), (6.65, 6.65), (6.85, 7.85)]
```

This is the result of binning qvalues that are within 10% of the qval_bin_size of the current max qval.

And from this, you can see that `6.45` and `6.65` are the qvals because these are "singular" bins, or "q-values that form their own bin" because they are too far aways from the previous or subsequent q-values. The `qval_extents` are the non-singular ranges.

Adding print-statements to the `pheweb` manhattan.py, I see that the `extents` for the
same region are:
```python
[(0.05, 4.75), (5.05, 6.25), (6.45, 6.45), (6.65, 6.65), (6.85, 7.85)]
```

so literally the same except for the 4.75 vs. 4.85.
Let me check the qvals. Ok, the qvals are different for this region, so this is
likely a result of different variants being added to this bin. So instead I'm going to check the variants that are being added to this bin.

I think this the binning is being done in the `_bin_variant` function, but this
is called by `_maybe_bin_variant` which is called by `_maybe_peak_variant` if
priority queue gets full. Actually I'm getting confused. The json file produced by
pheweb at `manhattan/Weight.json` doesn't have any actual position information, just
the qvals and qval_extents.

Actually, I'm wondering if the rounding of p_values to generate the `pheno_gz/` files
by pheweb is causing the slight differences. I reran spheweb on the `pheno_gz/` file
created by `pheweb` after gunzipping it.

Yes! That fixed the `qval_extents` difference!
I wonder if it will also fix the differences in the `unbinned_variants`, yes it has!
Ok, I think this means that the manhattan plots will be the same too! Let me check.

The Manhattan plots are NOT the same, comparing the Broad website `https://broad.io/dogPheweb` vs. the spheweb output, the actual loci are different, but comparing
the spheweb output to the pheweb output, the loci are the same! Must be some
difference between the "production" PheWeb and the local PheWeb, but I'm happy now.

I'm going to say that this is a win and the comparison is complete! The legacy
code will remain as part of the project for a while, and maybe forever, I will include
a small test file in the tests directory to allow the legacy code to be tested.

Ok, finished this on Sept 4th finally, pushed the `legacy_binning` to `dev`.
It was little enough work that I didn't make a new entry here for it.

Noticed, however, that although the generated json files are identical between
PheWeb and SpheWeb, the tables below the manhattan plots are NOT identical. So
there must be some logic that is performed in determining which variants are
shown in the table. Yes, there are actually only 96 variants shown in the table
for "dog weight" in PheWeb even though there are 596 unbinned variants that are
used for plotting. Ohh, this is controlled by the `{"peak": true}` field in the
dictionary of each variant!

This code is in the `populate_streamtable` function in `pheweb/serve/static/pheno.js`.

This was a good thing to learn, the variants listed in the table are only a
subset of the variants used to create the manhattan plot. I have to decide
if I want to implement this the same way in SpheWeb, but at least now I
understand PheWeb better.
