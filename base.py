# -*- coding: utf-8 -*-
"""
Created on 09.01.2019

@author: beckmann

Base to be added to the upper parts.
Upper parts are expected to be x,y = 40x40mm², i.e. the base starts at z=0, y=-20 and is symmetric in +-x

"global_settings.ini" controls which type of base is used for all parts.
"""

import configparser
import warnings

import numpy
from solid import *
from solid import translate, rotate, cylinder, cube

from helpers import rounded_plate, cyl_arc

__config = configparser.ConfigParser()
__config.read("global_settings.ini")
__threads20 = __config.getboolean("mount", "Threads20mm")
__rods30 = __config.getboolean("mount", "Rods6mmBy30mm")

if __rods30 and __threads20:
    print("bad configuration")
    exit()


def base():
    if __threads20:
        return base_threads20()

    if __rods30:
        return base_rods30()

    warnings.warn("No base configured, printed parts may be difficult to mount")


def base_threads20():
    return hole()(owis_holes(True))


def base_rods30(rod_sep = 30):
    """base for attaching to two parallel rods of 6mm diameter set 30mm apart."""
    mount_height = 10  # height (y) of mount
    single_clamp = translate((rod_sep/2, 0, 0))(single_rod_clamp())

    base = single_clamp + mirror((1, 0, 0))(single_clamp)

    r_arc = rod_sep/2  # TODO hardcoded
    arc_width = rod_sep+10-6*3  # TODO r*diam_hole of single_rod_clamp
    arc = cube((arc_width, mount_height, 10), center=True)
    arc -= translate((0, -r_arc + mount_height/4,0))(cylinder(r=r_arc, h=2*mount_height, center=True))

    base += arc

    base = translate((0, -20 - mount_height/2, 0))(base)

    return base


def single_rod_clamp(z_length=10):
    """single clamp to attach to a z-tube.
    The tube is at xy = (0,5), so that this clamp attaches to things at y=0...height"""
    diam_hole = 6
    clamp_diff = .5  # how much smaller is the clamp, i.e. how far does it need to bend?

    mount_height = 10  # height (y) of mount

    block = rounded_plate((2*diam_hole, mount_height, z_length), r=2)

    block += hole()(cylinder(d=diam_hole, h=2*z_length, center=True))
    block += hole()(translate((-clamp_diff/2, -mount_height//2, 0))(cube((diam_hole-clamp_diff, 10, 20), center=True)))  # "tunnel" for rod to slide into clip

    return block()


def owis_holes(move_to_minus_y=False):
    """
    Pair of holes for Owis 40, centered at x=y=0, extending upwards from z=0
    :param move_to_minus_y: Move holes to z=-20, i.e. for optical axis at z=0
    :return:
    """
    hole = owis23hole()
    owis_holes = translate([-10, 0, 0])(hole) + translate([10, 0, 0])(hole)  # z=0 is outside plane

    if move_to_minus_y:
        owis_holes = translate([0, -20, 0])(
            rotate([-90, 0, 0])(
                owis_holes
            )
        )
    return owis_holes


def owis23hole():
    """hole from below into z=0 plane, for M2.3 screws"""
    hole = cylinder(1, h=10, center=True)
    hole += translate([0, 0, -5])(
        cylinder(r1=2, r2=1, h=2, center=True)
    )
    return translate([0, 0, 5])(hole)


def owis_block():
    plate = cube([40, 40, 10], True)

    plate -= owis_holes(True)

    return plate


if __name__ == '__main__':
    upper = cube((40, 40, 10), center=True)

    scad_render_to_file(upper+base(), "scad/tests/base_demo.scad")