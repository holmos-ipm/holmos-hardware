# Holmos - Hardware

Holmos is a digital holographic microscope.
The [software repository](https://github.com/holmos-ipm/holmos-rpi/) has more information about the project.

This repository contains instructions to build your own copy of the setup, and files describing the 3D-printed parts.

If you want to be one of the first to build Holmos microscope, you can contact us.
We have a couple of complete kits (3D-printed and bought parts) that we can sell for <200 €.
This offer is valid until we run out of parts.

## Requirements

### Purchased parts
See [Teileliste](Teileliste.md)
The steel rods need to be 600 mm long if you are using the reference design.

### Download; what to print
Unless you want to modify things, you can download .STL files directly from the `reference_assembly` subfolder [here](reference_assembly/).
Your printer's software should be able to read them directly.
Print one of each file, and you'll have everything you need.

We developed this using Ultimaker printers and their [Cura](https://ultimaker.com/en/products/ultimaker-cura-software) software,
but any other printer should work.

### Assembly
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

## Modifying the 3D parts
To modify the parts, you'll need to compile from Python to SCAD to STL:

To get scad files:
* A clone of this repository
* Python (only tested for python 3)
* [Solidpython](https://solidpython.readthedocs.io/en/latest/) - usually available through `pip install solidpython`

To convert from scad to stl:
* [OpenSCAD](http://www.openscad.org)
