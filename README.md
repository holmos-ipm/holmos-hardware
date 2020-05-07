# Holmos - Hardware

Holmos is a digital holographic microscope.
The [software repository](https://github.com/holmos-ipm/holmos-rpi/) has more information about the project.

This repository contains instructions to build your own copy of the setup, and files describing the 3D-printed parts.

Unfortunately, shipping or selling kits is too complicated for our institute, so we cannot offer kits.

## Requirements

### Purchased parts
See [shopping list](shopping_list.md).
The steel rods need to be at least 600 mm long if you are using the reference design.

### Download; what to print
Unless you want to modify things, you can download .STL files directly from the `reference_assembly` subfolder [here](reference_assembly/).
Your printer's software should be able to read them directly.
Print one of each file, and you'll have everything you need.

If you are using parts with different diameters than the reference_assembly, modify the printable parts accordingly.

We developed this using Ultimaker printers and their [Cura](https://ultimaker.com/en/products/ultimaker-cura-software) software,
but any other printer should work.

### Assembly
Start by looking at `reference_assembly.py`.
It contains a list of parts, and their `z` positions along the optical axis.
Run the file, and it will generate a scad file showing the entire assembly (except rails).
In addition, a folder full of the individual parts is generated.
Print those parts, and assemble them at the positions given, and you should have a good starting point.

For instructions on individual parts, e.g. how to mount purchased parts in the printed mounts, see the [instructions folder](instructions).

### Adjustment, Usage
See [instructions/adjustment.md]() in this repository, or browse the [German student documentation](https://github.com/holmos-mikroskop/holmos/wiki)

## Optional parts
### Stability
Additional struts and crosses (e.g. Rpi_mount) can make the cage more stable.

### Light shield
A `round_mounts.round_mount_light(20, opening_angle=0, cyl_length=40, ring_thick=2)` can help shield the camera against stray light and make the setup work better in bright environments.

### Transport
The cage-based setup fits inside a tube (HT DN90).
To keep the setup from hitting the tube sides, print some `cage.cage_circumference()`
In a DN90 tube, the Raspberry Pi needs to be removed, and the movable mirror needs to be removed from the crane.
It can be stored in a `crane_mirror(mirror_offset_x=0, crane_only=True)` for transport.

## Tweaking
How tight the clips become depends on your printer, printer settings and the rods you are using.
`base.test_rod_clamp_tightness()` can be used to generate a test object with several clips.
Edit `Rods6mm_tightness` in `global_settings.ini`to change the fit globally.

## Modifying the 3D parts
To modify the parts, you'll need to compile from Python to SCAD to STL:

To re-create all parts, run
```
python reference_assembly.py
```
Be aware that this might take a long time (more than an hour) depending on the resolution you choose in OpenSCAD. You might need to install missing packages with `pip install <package>`. Also, make sure you have OpenSCAD installed in the location specified in `global_settings.ini`

To get scad files:
* A clone of this repository
* Python (only tested for python 3)
* [Solidpython](https://solidpython.readthedocs.io/en/latest/) - usually available through `pip install solidpython`

To convert from scad to stl:
* [OpenSCAD](http://www.openscad.org)
