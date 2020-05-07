# -*- coding: utf-8 -*-
"""
Created on 10.01.2019

@author: beckmann, bertz

Parts for Holmos holographic microscope.

All "final" functions - that is, parts that are supposed to be printed, need the keyword argument "assemble".
This way, the reference assembly and the bill of materials can be generated using the same functions.

If assemble=False, return the part so that it can be 3D-printed from z=0 upwards.
                   The printer bed is the xy-plane.
If assemble=True, return the part so that the optical axis is at z=0, with laser light traveling downwards
                  The table (or the RPi camera) is the xy plane
"""

from solid.utils import *  # pip install Solidpython
from solid import *  # pip install Solidpython
import numpy

from base import owis_holes, base, sunk_hole, base_rods30
from file_tools import safe_mkdir
from helpers import rounded_plate
from render_stl import render_scad_dir_to_stl_dir


def rpi_cam_mount(assemble=False):
    # https://www.raspberrypi.org/documentation/hardware/camera/mechanical/rpi_MECH_Camera2_2p1.pdf
    # 2016-11-30: printed; works. but: needs 4 spacers to keep the smd components on the back of the camera from touching the plate.
    rpi_thick = 3

    strut_y_end = 14.5
    struts_x = [-7.5, 7.5]
    strut_thick = 3

    base_thick = 5

    # base_plate = translate([0, -20+base_thick/2, 0])(cube([40, base_thick, 10], center=True))
    base_plate = translate([0, -20 + base_thick / 2, 0])(
        rotate([90, 0, 0])(
            rounded_plate([30, 10, base_thick], 2)
        )
    )
    base_plate += base()

    plate = translate([0, 0, -5])(rpi_cam_plate(rpi_thick))

    for strut_x in struts_x:
        strut = translate([strut_x, -(20 - strut_y_end) / 2, 0])(cube([strut_thick, 20 + strut_y_end, 10], center=True))
        cyl = rotate([0, 90, 0])(cylinder(r=10, h=50, center=True))  # cylinder along x-axis, in origin
        cyl = scale([1, (strut_y_end + 20 - base_thick) / 10, 1])(cyl)  # z=10, y = strut height
        cyl = translate([0, -20 + base_thick, -5])(cyl)  # axis into front top edge of base plate
        strut *= cyl
        plate += strut

    mount = base_plate + plate

    return mount


def rpi_cam_plate(thick=5):
    "plate for raspberry pi camera, with camera at [0,0,0], facing down"
    rpi_holes_x_2 = 21 / 2
    rpi_holes_y = 12.5

    rpi_border = 2
    rpi_ysize = 23.86
    rpi_ytop = 14.5
    rpi_xsize = 25

    gap_xsize = 11.5  # width for offset camera connector
    gap_ysize = 20

    plate_ycenter = rpi_ytop-rpi_ysize/2
    rpi_plate = rounded_plate((rpi_xsize, rpi_ysize, thick), rpi_border)
    rpi_plate = translate([0, plate_ycenter, thick / 2])(rpi_plate)  # one pair of holes (and camera) are at y=0
    rpi_plate -= translate((0, plate_ycenter, thick/2))(rounded_plate((gap_xsize, gap_ysize, 2*thick), 1))

    for x in [rpi_holes_x_2, -rpi_holes_x_2]:
        for y in [0, rpi_holes_y]:
            hole = translate([x, y, 0])(sunk_hole())
            rpi_plate -= hole
    return rpi_plate


def strut_with_holes(hole_dist, strut_thick, strut_width, hole_diam=2):
    """flat strut with two holes at y=+-hole_dist"""
    diag_strut = rounded_plate((strut_width, hole_dist + strut_width, strut_thick), strut_width / 2)
    for y in (hole_dist / 2, -hole_dist / 2):
        thread = sunk_hole(length=50, r=hole_diam/2)
        thread = hole()(thread)
        diag_strut += translate((0, y, -strut_thick / 2))(thread)
    return diag_strut


def slide_holder(assemble=True, angle_deg=0):
    """deg=0: "normal" orientation: slide is perpendicular to optical axis"""
    dov_h = 3
    dov_w0 = 5
    dov_w1 = 7
    dov_pad = .1

    base_thick = 5
    clamp_width = 8
    clamp_spacing = 40 - clamp_width
    clamp_base = 2
    clamp_reach = 20 - base_thick - clamp_base
    clamp_length = numpy.sqrt(2) * clamp_reach

    base_plate = translate([0, -(40 - base_thick) / 2, 0])(cube([40, base_thick, 10], center=True))
    base_plate += base()
    base_plate = rotate((0, angle_deg, 0))(base_plate)

    base_plate += translate([0, -(40 - base_thick) / 2, 0])(cube([40, base_thick, 10], center=True))

    clamp = translate([0, 0, -1])(slide_clamp(clamp_reach, clamp_length, base_height=clamp_base, width=clamp_width))

    # dovetail: parts touch at y=0, tail into -y
    trap_pts = [[dov_w0 / 2, 0], [-dov_w0 / 2, 0], [-dov_w1 / 2, -dov_h], [dov_w1 / 2, -dov_h]]
    trap_pts_padded = [[dov_w0 / 2 + dov_pad, .01], [-dov_w0 / 2 - dov_pad, .01],
                       [-dov_w1 / 2 - dov_pad, -dov_h - dov_pad], [dov_w1 / 2 + dov_pad, -dov_h - dov_pad]]
    trap_clear = [[dov_w0 / 4, -dov_h / 2], [-dov_w0 / 4, -dov_h / 2], [-dov_w1 / 4, -1.01 * dov_h],
                  [dov_w1 / 4, -1.01 * dov_h]]
    dov_section = polygon(trap_pts) - polygon(trap_clear)
    dov_section_pad = polygon(trap_pts_padded)

    dov = linear_extrude(height=clamp_width)(dov_section)
    dov_pad = linear_extrude(height=2 * clamp_width)(dov_section_pad)

    dov = rotate([0, 90, 0])(
        translate([0, 0, -clamp_width / 2])(dov)
    )
    clamp += translate([0, -clamp_reach - clamp_base, 0])(dov)

    dov_pad = rotate([0, 90, 0])(
        translate([0, 0, -clamp_width])(dov_pad)
    )
    base_plate -= translate([20, -clamp_reach - clamp_base, 0])(dov_pad)
    base_plate -= translate([-20, -clamp_reach - clamp_base, 0])(dov_pad)

    if assemble:
        clamps = translate([1.3 * clamp_spacing / 2, 0, 0])(clamp)
        clamps += translate([-clamp_spacing / 2, 0, 0])(clamp)
        base_plate += cylinder(d=1, h=1, center=True)  # visualize optical axis
        assembly = rotate((0, -angle_deg, 0))(base_plate + clamps)

    else:  # separate for printing
        clamp = translate([30, 0, (clamp_width-10)/2])(rotate((0, 90, 0))(clamp))
        clamps = clamp + mirror((1, 0, 0))(clamp)
        base_plate = rotate((-90, 0, 0))(translate((0, 20, 0))(base_plate))
        assembly = base_plate + clamps

    return assembly


def slide_clamp(clamping_reach, clamp_length, base_height=5, width=8):
    # single clamp to clamp a glass slide to the z=0 plane, open from +y
    gap_width = 0.5  # Kosmos glass: 1 mm
    back_thick = 4
    clip_thick = 1.5
    clip_wave = 4

    total_height = clamp_length + base_height
    clip_z_extent = clip_thick + clip_wave + gap_width
    total_thick = back_thick + clip_z_extent

    clip_ys = numpy.linspace(clamp_length - clamping_reach, -clamping_reach, 50)
    clip_xs = gap_width + clip_wave / 2 - clip_wave / 2 * numpy.cos(clip_ys / clamping_reach * numpy.pi)
    clip_ys = numpy.hstack([clip_ys, clip_ys[::-1]])
    clip_xs = numpy.hstack([clip_xs + clip_thick, clip_xs[::-1]])
    clip = polygon(list(zip(clip_xs, clip_ys)))
    clip = linear_extrude(height=width)(clip)
    clip = translate([width / 2, 0, 0])(rotate([0, -90, 0])(clip))

    back = translate([0, -total_height / 2 + (clamp_length - clamping_reach), -back_thick / 2])(
        cube([width, total_height, back_thick], center=True))
    base = translate([0, -clamping_reach - base_height / 2, (clip_z_extent - back_thick) / 2])(
        cube([width, base_height, back_thick + clip_z_extent], center=True))

    return clip + back + base


def objective_mount():
    """mount for microscope objective"""
    
    mount = rounded_plate([40, 40, 10], r=5)
    mount -= owis_holes(True)
    mount -= cylinder(d=20, center=True, h=11)
    
    return mount


def tube_with_rodmount():
    """base_plate with 3 clamps for new HolMOS-Cage"""
    
    mount = base_rods30(z_length=30)
    mount += translate((0,0,-15))(cylinder(d=43, h=30))
    mount += translate((0,-10,0))(cube((40,20,30), center=True))
    mount -= translate((0,0,-30))(cylinder(d=38, h=60))
    
    return mount


if __name__ == "__main__":

    _fine = True
    render_STL = False

    if _fine:
        header = "$fa = 5;"  # minimum face angle
        header += "$fs = 0.1;"  # minimum face size
    else:
        header = ""

    safe_mkdir("scad/misc")

    scad_render_to_file(slide_holder(False), "scad/misc/slide-holder.scad", file_header=header)
    scad_render_to_file(slide_holder(True), "scad/misc/slide-holder-assembled.scad", file_header=header)
    scad_render_to_file(slide_holder(False, 45), "scad/misc/beamsplitter-holder.scad", file_header=header)

    scad_render_to_file(rpi_cam_mount(), "scad/misc/RPi-Cam.scad", file_header=header)

    if render_STL:
        safe_mkdir("stl")
        render_scad_dir_to_stl_dir("scad/misc", "stl")



