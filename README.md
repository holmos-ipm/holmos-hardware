# holmos-hardware

Hardware for holmos - mostly Solidpython to generate scad

## Requirements
### Software
To get scad files:
* A clone of this repository
* Python (only tested for python 3)
* [Solidpython](https://solidpython.readthedocs.io/en/latest/) - usually available through `pip install solidpython`

To convert from scad to stl:
* [OpenSCAD](http://www.openscad.org)

And finally, you'll need to print the .stl files. 
We developed this using Ultimaker printers and their [Cura](https://ultimaker.com/en/products/ultimaker-cura-software) software, 
but any other printer should work.

### Purchased parts
See [Teileliste](Teileliste.md)

## What to print, and where to put it
Start by looking at `reference_assembly.py`. 
It contains a list of parts, and their `z` positions along the optical axis.
Run the file, and it will generate a scad file showing the entire assembly (except rails).
In addition, a folder full of the individual parts is generated.
Print those parts, and assemble them at the positions given, and you should have a good starting point.

## Tweaking
How tight the clips become depends on your printer, printer settings and the rods you are using.
`base.test_rod_clamp_tightness()` can be used to generate a test object with several clips.

