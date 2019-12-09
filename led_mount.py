# -*- coding: utf-8 -*-
from solid import *

import base
from file_tools import safe_mkdir
from render_stl import render_scad_dir_to_stl_dir


def hex_led_mount(assemble=True):
    """Mount for hexagonal LED.
    Desgined for https://www.luxeonstar.com/assets/downloads/ds23.pdf, because I found that LED.
    No idea how common/standardized these dimensions are among hexagonal LEDs.
    Printed 2019-12-09. Works, but not pretty: some clips break, but LED stays mounted."""

    # back of PCB is at z=0
    pcb_thick = 1.6
    r_hole_pos = 19/2
    n_holes = 6
    r_single_hole = 1.6

    backplate_thick = 4
    arrowhead_height = 2
    arrowhead_delta_r = .3

    plate = translate((0, 0, -backplate_thick/2))(cylinder(r=r_hole_pos+r_single_hole, h=backplate_thick, center=True))
    plate -= translate((0, 0, -backplate_thick/2))(cylinder(r=r_hole_pos-r_single_hole, h=2*backplate_thick, center=True))

    connector = cube((r_hole_pos, 20 - r_hole_pos, backplate_thick), center=True)
    connector = translate((0, -(20 + r_hole_pos)/2, -backplate_thick/2))(connector)

    plate += connector

    arrowhead = cylinder(r1=r_single_hole + arrowhead_delta_r, r2=r_single_hole-arrowhead_delta_r,
                         h=arrowhead_height, center=True)
    arrowhead = translate((0, 0, pcb_thick+arrowhead_height/2))(arrowhead)

    pin = translate((0, 0, -backplate_thick))(cylinder(r=r_single_hole, h=pcb_thick+backplate_thick))
    pin += arrowhead
    pin -= cube((4*r_single_hole, 4*arrowhead_delta_r, 2*(backplate_thick+arrowhead_height)), center=True)  # slit

    # move pin outside center and add at regular angles:
    pin = translate((r_hole_pos, 0, 0))(pin)
    for angle in (360/n_holes*i for i in range(n_holes)):
        plate -= rotate((0, 0, angle))(  # remove half of material to allow flexing of pin
            translate((r_hole_pos, 0, -backplate_thick/4.01))(  # .01 for non-identical surfaces
                cylinder(r=(2*r_single_hole), h=backplate_thick/2, center=True))
        )
        plate += rotate((0, 0, angle))(pin)  # actual pin

    clip = base.base(z_length=2*backplate_thick)

    return clip + plate


if __name__ == '__main__':
    header = "$fa = 5;"  # minimum face angle
    header += "$fs = 0.1;"  # minimum face size

    scad_path = "scad/misc/"
    stl_path = "stl/misc/"
    safe_mkdir(scad_path)

    scad_render_to_file(hex_led_mount(),
                        scad_path + "hex_led.scad", file_header=header)

    safe_mkdir(stl_path)
    render_scad_dir_to_stl_dir(scad_path, stl_path)
