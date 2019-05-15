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
__rods30_tightness = __config.getfloat("mount", "Rods6mm_tightness")

rods30_dist_third_rod = 60  # distance of third rod behind two main rods (orthogonal distance)
rods30_diag_third_rod = (15**2 + rods30_dist_third_rod**2)**.5

if __rods30 and __threads20:
    print("bad configuration")
    exit()


def base(**kwargs):
    if __threads20:
        return base_threads20()

    if __rods30:
        return base_rods30(**kwargs)

    warnings.warn("No base configured, printed parts may be difficult to mount")


def base_threads20():
    return hole()(owis_holes(True))


def base_rods30(rod_sep=30, z_length=10):
    """base for attaching to two parallel rods of 6mm diameter set 30mm apart."""
    mount_height = 10  # height (y) of mount
    single_clamp = translate((rod_sep/2, 0, 0))(single_rod_clamp(z_length))

    base = single_clamp + mirror((1, 0, 0))(single_clamp)

    r_arc = (rod_sep**2-20**2)**.5  # TODO hardcoded
    arc_width = rod_sep+10-6*3  # TODO r*diam_hole of single_rod_clamp
    arc = cube((arc_width, mount_height, z_length), center=True)
    arc -= translate((0, -r_arc + mount_height/4,0))(cylinder(r=r_arc, h=4*z_length, center=True))

    base += arc

    base = translate((0, -20 - mount_height/2, 0))(base)

    return base


def single_rod_clamp(z_length=10, tightness=__rods30_tightness):
    """single clamp to attach to a z-tube.
    The tube is at xy = (0,5), so that this clamp attaches to things at y=0...height
    :param tightness: diameter reduction of clamp. larger values give tighter fit."""

    diam_hole = 6 - tightness
    clamp_diff = .5  # how much smaller is the clamp, i.e. how far does it need to bend?

    mount_height = 10  # height (y) of mount

    block = rounded_plate((2*diam_hole, mount_height, z_length), r=2)

    block += hole()(cylinder(d=diam_hole, h=5*z_length, center=True))
    block += hole()(translate((-clamp_diff/2, -mount_height//2, 0))(cube((diam_hole-clamp_diff, 10, 2*z_length), center=True)))  # "tunnel" for rod to slide into clip

    return block()


def owis_holes(move_to_minus_y=False):
    """
    Pair of holes for Owis 40, centered at x=y=0, extending upwards from z=0
    :param move_to_minus_y: Move holes to z=-20, i.e. for optical axis at z=0
    :return:
    """
    hole = sunk_hole()
    owis_holes = translate([-10, 0, 0])(hole) + translate([10, 0, 0])(hole)  # z=0 is outside plane

    if move_to_minus_y:
        owis_holes = translate([0, -20, 0])(
            rotate([-90, 0, 0])(
                owis_holes
            )
        )
    return owis_holes


def sunk_hole(r=1, length=10):
    """
    Hole from below into z=0 plane. Countersunk: larger diameter at beginning, for easier insertion.
    :param r: Default: r=1 for M2.3 screws
    :param length:
    :return:
    """
    hole = translate([0, 0, length/2])(cylinder(r, h=length, center=True))
    hole += cylinder(r1=2*r, r2=r, h=1.4*r, center=True)
    return hole


def test_rod_clamp_tightness(tightnesses):
    """
    A series of clamps with different tightnesses, to find best value for given printer/rod combination
    :param tightnesses: list of tightnesses to try
    :return: object
    Printed 2019-08-05 with [0, 0.05, 0.10]. Works. 0.05 is barely noticeable; 0.10 definitely tighter.
    """
    spacing = 15
    base_height = 20

    n_tight = len(tightnesses)
    width = spacing * n_tight
    assembly = translate((width/2, base_height/2, 0))(cube((width, base_height, 10), center=True))
    for n, tight in enumerate(tightnesses):
        clamp = (single_rod_clamp(tightness=tight))  # add clamp with varying tightness
        label = rotate((0, 0, 90))(
                linear_extrude(height=.5, center=True)(
                    text("{:.2f}".format(tight), valign="center", halign="left", size=5., segments=1,
                         font="Liberation Sans:style=Bold")
                )
            )
        label = translate((.5, base_height/2, 5))(label)
        assembly += translate(((n+.5)*spacing, -5, 0))(clamp + label)

    return assembly


if __name__ == '__main__':
    header = "$fa = 5;"  # minimum face angle
    header += "$fs = 0.1;"  # minimum face size

    upper = cube((40, 40, 10), center=True)

    scad_render_to_file(upper+base(), "scad/tests/base_demo.scad", file_header=header)

    scad_render_to_file(base_rods30(z_length=100), "scad/label_100.scad", file_header=header)  # Long plate for sticker

    scad_render_to_file(test_rod_clamp_tightness([0, .05, .1]), "scad/tests/test_clamp_tightness.scad", file_header=header)