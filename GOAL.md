Thoughts on what I'd like SpheWeb to do
---

[PheWeb](https://github.com/statgen/pheweb) and 
[PheWeb2](https://github.com/GaglianoTaliun-Lab/PheWeb2)
already provide python packages that make it easy to share
and browse GWAS analyses.

The way these packages work is that they have a "process"
step which creates files needed for step two of "serving"
a flask website. This works well and is professional, but
it requires and actively running flask server.

For scientists and academics, however, finding funding time
and expertise to host a server is not always simple. If a publication
wants to make their GWAS results browsable they need to decide how
to host a server and how long they should support it.

Also, I have been part of a project where collaborators wanted to be
able to browse the GWAS data we were producing and this required setting up
a server. It was a fair amount of work to setup for an informal way of
sharing results with collaborators.

What has inspired me to try and make the static pheweb is that
it would be easier for academics to either create a static website that
could just be put on AWS S3 or some other cheap option, or maybe even
better if there could be a searchable PDF that has enough of the functionality
of PheWeb to still be useful without being too large of a file size.

There was a discussion already on PheWeb github issues about this
https://github.com/statgen/pheweb/issues/132 where one of the maintainers
explains that currently PheWeb might be able to be made static with tools
like frozen-flask but it would not be ideal:

> If you prevent scrolling/zooming the Locuszoom region plots and limit the
> autocomplete search box to only suggest gene names and phenotypes (and no
> longer suggest rsids or variants), the site could be converted to static
> files using wget or a dedicated archiving tool. If you want to attempt it I
> can show you which lines of code to remove to implement those changes. It
> would take a lot more storage space— perhaps 100x what it does now due to
> storing the same html over and over and storing overlapping Locuszoom plots.
> The storage issue could be mitigated with some shared JavaScript that wrote
> the DOM and a clever solution to the overlapping-plots issue.
> I recommend a webserver. It should run fine on the $5/month plan from
> DigitalOcean, plus storage cost. The Readme has instructions on reducing
> storage use.

I am imagining that the users of spheweb will have input files similar to PheWeb,
tabular results from running GWAS on multiple samples, and could run `spheweb build pdf`
or `sheweb build static-content` or similar. Better if they can `uvx spheweb`.

I want to make it easy to use spheweb with sensible defaults and be easy for a
biologist to use who has minor expertise in coding. I guess in this current setup
they would still need to use a command line but maybe this is ok for now since
they have likely needed to use the command line to run GWAS tools in the first place.

I would like to have a good tutorial that uses publically available GWAS data and
could be followed by a user or an AI agent since that might be more common in the
future. It would be ok to use fake simulated data for the tutorial.



