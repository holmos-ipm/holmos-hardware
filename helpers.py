# -*- coding: utf-8 -*-
"""
Created on 02.01.2019

@author: beckmann
"""
import numpy
from solid import translate, cube, rotate, union, cylinder

from solid.utils import *  # pip install Solidpython


def cyl_arc(r, h, a0, a1):
    solid_arc_length = (a1-a0) % 360  # mod360 e.g. for -10..10 -> arc is
    if solid_arc_length == 0:
        return cylinder(r,h,center=True)

    if solid_arc_length < 180:
        return cyl_arc_lt_180(r, h, a0, a1)
    else:
        return cylinder(r, h, center=True) - cyl_arc_lt_180(2*r, 2*h, a1, a0)  # slightly inefficient: subracting part could be simpler.


def cyl_arc_lt_180(r, h, a0, a1):
    # centered arc section of cylinder, for angles up to 180deg
    positive_y_plane = translate([0, 2 * r, 0])(cube([4 * r, 4 * r, 2 * h], center=True))
    result = cylinder(r, h, center=True)
    result *= positive_y_plane  # keep 0...180
    result = rotate([0, 0, -(a1 - a0)])(result)
    result -= positive_y_plane  # keep 0...a1-a0
    return rotate([0, 0, a1])(result)


if __name__ == "__main__":
    import os

    if not os.path.exists("scad"):
        os.mkdir("scad")
    if not os.path.exists("scad/tests"):
        os.mkdir("scad/tests")

    tests = {"cyl_arc - thin pie slice": cyl_arc(50, 10, -30, -10),
             "cyl_arc - pacman": cyl_arc(50, 10, 30, -30)}

    for label in tests:
        filename = os.path.join("scad", "tests", label + ".scad")
        scad_render_to_file(tests[label], filename)


def hexagon(diam, height):
    """diam: smallest diameter, distance between parallel sides"""
    n=6
    facewidth = diam*numpy.tan(numpy.pi/n)
    single_box = translate((-diam/4, 0, 0))(cube((diam/2, facewidth, height), center=True))
    boxes = []
    for i in range(n):
        boxes.append(rotate((0, 0, 360*i/n))(single_box))
    return union()(boxes)


def rounded_plate(xyz, r):
    '''centered plate with rounded (xy) corners'''
    x, y, z = xyz

    cube_x = cube([x - 2 * r, y, z], center=True)
    cube_y = cube([x, y - 2 * r, z], center=True)

    plate = cube_x + cube_y

    dx, dy = x / 2 - r, y / 2 - r
    for x, y in [[dx, dy],
                 [-dx, dy],
                 [-dx, -dy],
                 [dx, -dy]]:
        plate += translate([x, y, 0])(cylinder(r=r, h=z, center=True))

    return plate