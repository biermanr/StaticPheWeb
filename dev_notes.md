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
