# -*- coding: utf-8 -*-
"""
Created on 08.01.2019

@author: beckmann
"""
import numpy
from solid import scad_render_to_file, translate, rotate, cylinder, cube, linear_extrude, text

from base import base
from file_tools import safe_mkdir
from helpers import rounded_plate, cyl_arc, hexagon
from render_stl import render_scad_dir_to_stl_dir


def round_mount_light(inner_diam=17.9, ring_thick=3, opening_angle=30, stop_inner_diam=None, cyl_length=10,
                      clip_length=10, assemble=False):
    """
    mount for cylinder centered on optical axis (z). If opening_angle is None, clamping tabs are added.
    defaults: mount for Kosmos objective
    :param inner_diam: usually diameter of thing to be mounted
    :param ring_thick: thickness of ring determines stiffness
    :param opening_angle: ring is opened from -angle to +angle
    :param stop_inner_diam: if not None, a smaller second cylinder acts as a stop, i.e. for a lens.
    :param cyl_length: Total length of cylinder (including optional stop)
    :param clip_length: Length of clip. increase for heavy objects, e.g. objective with steel housing
    :param assemble:
    :return: Scad object
    """
    base_thick = 5
    connector_w = 3
    z_thick = 10  # thickness/z-length of entire assembly
    z_think_inner = 2

    do_clamp = False
    if opening_angle is None:
        do_clamp = True
        opening_angle = 0

    base_plate = translate([0, -20 + base_thick / 2, 0])(
        rotate([90, 0, 0])(
            rounded_plate([30, 10, base_thick], 4)
        )
    )
    base_plate += translate((0, 0, (clip_length-10)/2))(base(z_length=clip_length))

    outer_diam = inner_diam+2 * ring_thick
    ring = cyl_arc(r=outer_diam/2, h=cyl_length, a0=90+opening_angle, a1=90-opening_angle)
    ring = translate((0, 0, (cyl_length-z_thick)/2))(ring)
    if stop_inner_diam is None:
        ring -= cylinder(d=inner_diam, h=2*cyl_length, center=True)
    else:
        ring -= cylinder(d=stop_inner_diam, h=2*cyl_length, center=True)
        ring -= translate((0,0,z_think_inner))(cylinder(d=inner_diam, h=z_thick, center=True))

    if do_clamp:  # clamps with holes extending towards +y
        hex_diam = 5.5  # M3 nut
        clamp_extension = hex_diam + 2
        hole_diam = 3.5
        clamp_length = ring_thick+clamp_extension
        single_clamp = rounded_plate((clamp_length, z_thick, ring_thick), True)
        through_nut_hole = cylinder(d=hole_diam, h=2*ring_thick, center=True)
        through_nut_hole += translate((0, 0, ring_thick/2))(hexagon(hex_diam, ring_thick/3))
        single_clamp -= translate([ring_thick/2, 0, 0])(through_nut_hole)

        ring -= translate([0, inner_diam, 0])(cube([ring_thick, 2*inner_diam, 2*cyl_length], center=True))  # slit
        ring += translate([ring_thick, inner_diam/2 + clamp_length/2, 0])(rotate([90, 0, 90])(single_clamp))
        ring += translate([-ring_thick, inner_diam/2 + clamp_length/2, 0])(rotate([-90, 0, 90])(single_clamp))

    connector_h = (40 - inner_diam) / 2
    connector_yc = inner_diam / 2 + connector_h / 2
    connector_xc = min(inner_diam/2, 5)
    connector = translate([connector_xc, -connector_yc, 0])(cube([connector_w, connector_h, z_thick], center=True))
    connector += translate([-connector_xc, -connector_yc, 0])(cube([connector_w, connector_h, z_thick], center=True))

    label = "d = {:.1f}".format(inner_diam)
    info_text = linear_extrude(height=.5, center=True)(
                    text(label, valign="center", halign="center", size=3., segments=1,
                         font="Liberation Mono:style=Bold")
                )

    base_plate += translate((0, -(20-base_thick/2), z_thick/2))(info_text)

    mount = base_plate + ring + connector

    if assemble:
        mount = rotate((0, 180, 0))(mount)

    return mount


if __name__ == '__main__':

    """
    https://forscherladen.lafeo.de/opti-media-achromat-2-linser-f-99-6-mm::10-550.OAL.html
    Durchmesser: 26,0 mm   # wrong; measured 24.3 mm -> 1"
    Brennweite: + 99,6 mm
    
    https://forscherladen.lafeo.de/opti-media-linse-nr.5-brennweite-65-mm::10-306.OML.html
    Durchmesser: 16,5 mm
    Brennweite: + 65 mm
    """

    header = "$fa = 5;"  # minimum face angle
    header += "$fs = 0.1;"  # minimum face size

    scad_path = "scad/misc/"
    stl_path = "stl/misc/"
    safe_mkdir(scad_path)

    scad_render_to_file(round_mount_light(20, opening_angle=None, stop_inner_diam=19),
                        scad_path + "objective_mount_edmund4x_simple.scad", file_header=header)

    scad_render_to_file(round_mount_light(24, opening_angle=None, stop_inner_diam=21),
                        scad_path + "objective_mount_edmund4x_plan.scad", file_header=header)

    scad_render_to_file(round_mount_light(20, opening_angle=0, cyl_length=40, ring_thick=2),
                        scad_path + "light_tube.scad", file_header=header)

    scad_render_to_file(round_mount_light(5, opening_angle=None), scad_path + "round_5mm_LED.scad", file_header=header)

    # with stop - lenses
    for d in (25.4, 20, 16.5):
        scad_render_to_file(round_mount_light(d, opening_angle=None, stop_inner_diam=d-2),
                            scad_path + "lens mount_d{:.1f}.scad".format(d), file_header=header)

    # without stop - lasers
    for d in (12, 10):
        scad_render_to_file(round_mount_light(d, opening_angle=None),
                            "scad/misc/round_mount_d{:.1f}.scad".format(d), file_header=header)

    safe_mkdir(stl_path)
    render_scad_dir_to_stl_dir(scad_path, stl_path)
