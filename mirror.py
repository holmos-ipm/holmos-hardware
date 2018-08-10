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
        self.center_thick = 4
        self.flexure_thick = 1  # smallest cross-section of flexure
        self.spring_thick = .6  # smallest thickness of spring
        self.gap = 2  # size of gap(s) between parts
        self.front_frame_thickness = 12

        self.screw_diam = 3.5
        self.hex_width = 5.5

    def thicknesses(self):
        pre_tilt_depth = numpy.arctan(numpy.deg2rad(self.pre_tilt_deg)) * self.center_size * numpy.sqrt(2)  # protrusion of center plate due to pre-tilt
        front_frame_thickness = self.front_frame_thickness
        back_wall_thickness = self.thickness - front_frame_thickness
        if back_wall_thickness < 2*self.gap:
            print(back_wall_thickness)
            warnings.warn("Back wall is only %.1f thick".format(back_wall_thickness))
        return pre_tilt_depth, front_frame_thickness, back_wall_thickness

    def front_plate_flex_corner(self):
        pre_tilt_depth, front_frame_thick, _ = self.thicknesses()
        front_frame = translate((0,0,-front_frame_thick/2))(
            cube((self.frame_size, self.frame_size, front_frame_thick), center=True)
        )

        front_frame -= cube((self.center_size+2*self.gap, self.center_size+2*self.gap, 4*front_frame_thick), center=True)

        # central plate
        center_plate = self.center_plate()

        # rotate central plate about its +x, +y corner, tilting the -x,-y corner inward.
        center_plate = translate((self.center_size/2, self.center_size/2, 0))(
            rotate((self.pre_tilt_deg/numpy.sqrt(2), -self.pre_tilt_deg/numpy.sqrt(2)), 0)(
                translate((-self.center_size/2, -self.center_size/2, 0))(
                    center_plate
                )
            )
        )

        # two flexure struts in (+x, +y) corner (single strut allows rotation about z)
        flexure_length = self.frame_size/2
        tr_x = (self.frame_size - flexure_length)/2
        tr_y = (self.center_size - self.flexure_thick)/2 - 2*self.gap

        for tr_x, tr_y, rot in (tr_x, tr_y, 0),(tr_y, tr_x, 90):  # first xy, then switched yx
            center_plate += translate((tr_x, tr_y, -self.center_thick - self.flexure_thick))(
                rotate((0,0,rot))(
                    cube((flexure_length, self.flexure_thick, self.flexure_thick), center=True)
                )
            )

        return front_frame + center_plate

    def center_plate(self):
        """central plate, not tilted."""
        return translate((0, 0, -self.center_thick / 2))(
            cube((self.center_size, self.center_size, self.center_thick), center=True)
        )

    def front_plate_three_springs(self, sep_for_print=True):
        center_plate = self.center_plate()
        spring_group = self.spring_group(sep_for_print)
        center_plate += spring_group
        center_plate += rotate((0,0,90))(spring_group)
        center_plate += rotate((0,0,-90))(spring_group)

        screw_center_xy = self.center_size/2 - self.gap
        for x,y in (screw_center_xy, -screw_center_xy), (-screw_center_xy, screw_center_xy),\
                   (screw_center_xy, screw_center_xy), (-screw_center_xy, -screw_center_xy):
            center_plate += translate((x,y,-self.center_thick/2))(
                cylinder(d=2.5*self.screw_diam, h=self.center_thick, center=True))
            center_plate -= translate((x,y,0))(cylinder(d=self.screw_diam, h=10*self.thickness, center=True))
            hex_depth=1
            center_plate -= translate((x, y, hex_depth/2))(
                hexagon(self.hex_width, 2*hex_depth)
            )

        return center_plate

    def spring_group(self, sep_for_print):
        """leaf spring outside +x +y corner of center plate"""
        sq2 = numpy.sqrt(2)
        strut_length = self.frame_size/sq2-self.gap  # diagonal
        strut_thick = self.center_thick
        strut_width = self.center_thick
        strut = translate((strut_length/2, 0, -strut_thick/2))(
            cube((strut_length, strut_width, strut_thick), center=True)
        )  # strut in +x orientation, one end at origin
        strut_y = (self.gap + strut_width)/2
        strut = translate((0, strut_y, 0))(strut) + translate((0, -strut_y, 0))(strut)  # two struts with gap

        # single spring
        _, front_frame_thickness, _ = self.thicknesses()
        spring_extrusion = (self.frame_size - self.center_size)/2 - self.gap
        spring_height = front_frame_thickness - strut_thick
        spring_width = spring_height  # should not exceed spring height if printing upright
        spring = translate((0, strut_width, -strut_thick-spring_height/2))(
            self.single_spring(spring_extrusion, spring_height, spring_width)
        )
        springs = spring + mirror((0,1,0))(spring)  # spring pair

        # add mounting
        shoulder_thick = self.spring_thick
        springs += translate((0, 0, - strut_thick/2))(cube((spring_extrusion, 0.95*self.gap, strut_thick), center=True))
        # shoulder/bottom plate
        springs += translate((0, 0, - strut_thick-shoulder_thick/2))(cube((spring_extrusion, 2*strut_width+self.gap, shoulder_thick), center=True))
        #springs += translate((0, 0, - strut_thick - spring_height+shoulder_thick/2))(cube((spring_extrusion, 2*self.gap, shoulder_thick), center=True))

        # up to here: springs with cube at origin
        if sep_for_print:
            springs = rotate((0, -90, 0))(springs)
            springs = translate((spring_extrusion+self.gap, 0, spring_extrusion/2-self.center_thick))(springs)
        springs = translate((strut_length-spring_extrusion/2, 0, 0))(springs)

        group = strut + springs
        group = rotate((0, 0, 45))(group)

        return group

    def single_spring(self, spring_extrusion, spring_height, spring_width):
        """one-sided spring, centered in z, for connection at y=0, flexing into +y, centered/extruded in x"""
        phis = numpy.linspace(-.66*numpy.pi, .5*numpy.pi, 50)
        xs_out = spring_width/2*numpy.cos(phis)
        ys_out = spring_height/2*numpy.sin(phis)

        xs_in = (spring_width/2-self.spring_thick)*numpy.cos(phis)
        ys_in = (spring_height/2-self.spring_thick)*numpy.sin(phis)

        points_out = list(zip(xs_out, ys_out))
        points_in = list(zip(xs_in, ys_in))
        points_in.reverse()
        spring_profile = polygon(points_out + points_in)

        spring = linear_extrude(height=spring_extrusion)(spring_profile)
        spring = rotate((0,0,90))(spring)
        spring = rotate((0,90,0))(spring)
        spring = translate((-spring_extrusion / 2, 0, 0))(spring)  # center in x
        return spring

    def back_frame(self):
        _, front_frame_thick, back_thick = self.thicknesses()
        back_frame = translate((0, 0, -back_thick/2 -front_frame_thick))(
            cube((self.frame_size, self.frame_size, back_thick), center=True)
        )

        # flexure is at +x,+y
        screw_center_xy = self.center_size/2 - self.gap
        for x,y in (screw_center_xy, -screw_center_xy), (-screw_center_xy, screw_center_xy),\
                   (screw_center_xy, screw_center_xy), (-screw_center_xy, -screw_center_xy):
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
    front = mount.front_plate_flex_corner() - translate((0, 0, -10))(owis_holes(move_to_minus_y=True))
    front = mount.front_plate_three_springs(sep_for_print=False)
    front_print = mount.front_plate_three_springs()
    back = mount.back_frame() - translate((0,0,-10))(owis_holes(move_to_minus_y=True))
    scad_render_to_file(front + back, "scad/mirror_mount.scad", file_header=header)
    scad_render_to_file(back, "scad/mirror_mount_back.scad", file_header=header)
    scad_render_to_file(front_print, "scad/mirror_mount_front.scad", file_header=header)