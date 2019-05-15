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
The steel rods need to be 600 mm long if you are using the reference design.

## What to print, and where to put it
Start by looking at `reference_assembly.py`. 
It contains a list of parts, and their `z` positions along the optical axis.
Run the file, and it will generate a scad file showing the entire assembly (except rails).
In addition, a folder full of the individual parts is generated.
Print those parts, and assemble them at the positions given, and you should have a good starting point.

## Optional parts
### Stability
Additional struts and crosses can make the cage more stable.

### Mounting
The `cage.board_hook()` can be used to hang the setup from a wall instead of mounting it to a surface.
To keep the cage stable at a useful distance from the wall, a `test_rod_clamp_tightness()` with three clips can be used.

### Light shield
A `lens_mounts.round_mount_light(20, opening_angle=0, cyl_length=40, ring_thick=2)` can help shield the camera against stray light and make the setup work better in bright environments.

### Transport
The cage-based setup fits inside a tube (HT DN90).
To keep the setup from hitting the tube sides, print some `cage.cage_circumference()`
In a DN90 tube, the Raspberry Pi needs to be removed, and the movable mirror needs to be removed from the crane.
It can be stored in a `crane_mirror(mirror_offset_x=0, crane_only=True)` for transport.

## Tweaking
How tight the clips become depends on your printer, printer settings and the rods you are using.
`base.test_rod_clamp_tightness()` can be used to generate a test object with several clips.

