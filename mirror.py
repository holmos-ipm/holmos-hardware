# -*- coding: utf-8 -*-
"""

"""

import warnings
from solid.utils import *  # pip install Solidpython
import numpy

from Holmos import owis_block, owis_holes


class MirrorMount:
    """
    Mirror mount, tiltable in two axes.
    One corner is fixed, two corners are pushed forward by screws.
    Coordinate system: mirror faces towards +z at z=0. Square mount, centered at x=y=0
    """

    def __init__(self):
        self.pre_tilt_deg = 5
        self.thickness = 15
        self.frame_size = 40  # length of sides of outer frame (square)
        self.center_size = 30  # length of sides of movable square
        self.center_thick = 2
        self.flexure_thick = 1  # smallest cross-section of flexure
        self.gap = 2  # size of gap(s) between parts

        self.screw_diam = 3.5
        self.hex_width = 5.5

    def thicknesses(self):
        pre_tilt_depth = numpy.arctan(numpy.deg2rad(self.pre_tilt_deg)) * self.center_size * numpy.sqrt(2)  # protrusion of center plate due to pre-tilt
        front_frame_thickness =  pre_tilt_depth + self.gap
        back_wall_thickness = self.thickness - front_frame_thickness
        if back_wall_thickness < 2*self.gap:
            print(back_wall_thickness)
            warnings.warn("Back wall is only %.1f thick".format(back_wall_thickness))
        return pre_tilt_depth, front_frame_thickness, back_wall_thickness

    def front_plate(self):
        pre_tilt_depth, front_frame_thick, _ = self.thicknesses()
        front_frame = translate((0,0,-front_frame_thick/2))(
            cube((self.frame_size, self.frame_size, front_frame_thick), center=True)
        )

        front_frame -= cube((self.center_size+2*self.gap, self.center_size+2*self.gap, 4*front_frame_thick), center=True)

        # central plate
        center_plate = translate((0, 0, -self.center_thick/2))(
            cube((self.center_size, self.center_size, self.center_thick), center=True)
        )

        # rotate central plate about its +x, +y corner, tilting the -x,-y corner inward.
        center_plate = translate((self.center_size/2, self.center_size/2, 0))(
            rotate((self.pre_tilt_deg/numpy.sqrt(2), -self.pre_tilt_deg/numpy.sqrt(2)), 0)(
                translate((-self.center_size/2, -self.center_size/2, 0))(
                    center_plate
                )
            )
        )

        # diagonal flexure strut to hold plate, connected to bottom of center plate
        flexure_length = numpy.sqrt(2) * (self.center_size/2 + self.gap)
        center_plate += translate((flexure_length/numpy.sqrt(2)/2,
                                   flexure_length/numpy.sqrt(2)/2,
                                   -self.center_thick - self.flexure_thick))(
            rotate((0,0,45))(
                cube((flexure_length, self.flexure_thick, 2*self.flexure_thick), center=True)
            )
        )

        return front_frame + center_plate

    def back_frame(self):
        _, front_frame_thick, back_thick = self.thicknesses()
        back_frame = translate((0, 0, -back_thick/2 -front_frame_thick))(
            cube((self.frame_size, self.frame_size, back_thick), center=True)
        )

        # flexure is at +x,+y
        screw_center_xy = self.center_size/2 - self.gap
        for x,y in (screw_center_xy, -screw_center_xy), (-screw_center_xy, screw_center_xy):
            back_frame -= translate((x,y,0))(cylinder(d=self.screw_diam, h=10*self.thickness, center=True))
            hex_depth = self.gap
            back_frame -= translate((x, y, -front_frame_thick-hex_depth/2))(
                hexagon(self.hex_width, 2*hex_depth)
            )

        return back_frame


def hexagon(diam, height):
    """diam: smallest diameter, distance between parallel sides"""
    n=6
    facewidth = diam*numpy.tan(numpy.pi/n)
    single_box = translate((-diam/4, 0, 0))(cube((diam/2, facewidth, height), center=True))
    boxes = []
    for i in range(n):
        boxes.append(rotate((0, 0, 360*i/n))(single_box))
    return union()(boxes)


if __name__ == "__main__":
    import os
    _fine = True

    if _fine:
        header = "$fa = 5;"  # minimum face angle
        header += "$fs = 0.1;"  # minimum face size
    else:
        header = ""

    if not os.path.exists("scad"):
        os.mkdir("scad")

    mount = MirrorMount()
    front = mount.front_plate() - translate((0,0,-10))(owis_holes(move_to_minus_y=True))
    back = mount.back_frame() - translate((0,0,-10))(owis_holes(move_to_minus_y=True))
    scad_render_to_file(front + back, "scad/mirror_mount.scad", file_header=header)
    scad_render_to_file(back, "scad/mirror_mount_back.scad", file_header=header)
    scad_render_to_file(front, "scad/mirror_mount_front.scad", file_header=header)