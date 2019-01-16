# -*- coding: utf-8 -*-
"""
Created on 10.01.2019

@author: beckmann
"""
import itertools
import warnings

import numpy

from solid import *

from base import base, hole23, single_rod_clamp
from helpers import rounded_plate


def crane_45deg_mirror():
    """Mount for 45deg movable mirror"""
    screw_dist_from_center = 30/2/2**.5  # Four holes on circle d=30
    mirror_plate_wh = 30
    thick = 10
    mirror_offset = 35  # TODO: calc
    dist_to_cam = 300

    mirror_angle_deg = -numpy.rad2deg(numpy.arctan(mirror_offset/dist_to_cam))/2

    plate = rounded_plate((40, 40, thick), 2)
    plate -= rounded_plate((30, 30, 2*thick), 2)

    mirror_plate_blank = rounded_plate((mirror_plate_wh, mirror_plate_wh, thick), 2)
    mirror_plate_blank += hole()(cylinder(d=20, h=2*thick, center=True))

    mirror_plate_threads = mirror_plate_blank
    for (x,y) in itertools.product((1, -1), (1,-1)):
        thread = hole()(rotate((0, 180, 0))(hole23()))  # from above into z=0
        mirror_plate_threads += translate((x*screw_dist_from_center, y*screw_dist_from_center, thick/2))(thread)

    mirror_plate_threads = rotate((0, mirror_angle_deg, 0))(mirror_plate_threads)
    mirror_plate_threads = translate((0, 0, 40*numpy.tan(numpy.deg2rad(-mirror_angle_deg))))(mirror_plate_threads)

    plate += translate((mirror_offset, 0, 0))(mirror_plate_blank)
    plate += translate((mirror_offset, 0, 0))(mirror_plate_threads)

    plate += base()

    return plate


def crane_mirror(assemble=True):
    """Mount for 45deg movable mirror
    assemble=True: put things where they're supposed to go
    assemble=False: put things on printer bed"""
    thick = 10
    mirror_offset_x = 25  # TODO: calc
    dist_to_cam = 200
    #dist_to_cam = 30

    arm_width = 5.5
    mirror_z = 17

    rod_thick = 6
    rod_to_mirror = 2*arm_width

    deflection_angle_rad = numpy.pi/2+numpy.arctan(mirror_offset_x/dist_to_cam)
    mirror_angle_rad = deflection_angle_rad/2

    rod_z = mirror_z - rod_to_mirror*numpy.cos(mirror_angle_rad)   # z-height of rod for y-rotation
    rod_x = mirror_offset_x + rod_to_mirror*numpy.sin(mirror_angle_rad)

    plate = rounded_plate((40, 40, thick), 2)
    plate -= translate((10,0,0))(rounded_plate((50, 30, 2*thick), 2))

    arm_length = rod_x-20
    clip_arm = cube((arm_length+arm_width, thick, arm_width), center=True)  # thick <-> width because rotated x<->z
    clip_arm = rotate((90, 0, 0))(clip_arm)
    clip_arm = translate((arm_length/2+20, 20-arm_width/2, 0))(clip_arm)
    clip_arm += translate((rod_x, 20-arm_width/2, rod_z))(rotate((-90, 0, 0))(single_rod_clamp(arm_width)))

    plate += clip_arm
    plate += mirror((0, 1, 0))(clip_arm)

    mirror_intermediate = crane_mirror_intermediate(rod_thick, arm_width, rod_to_mirror, assemble)

    if assemble:
        plate += translate((rod_x, 0, rod_z))(
            rotate((0, -numpy.rad2deg(mirror_angle_rad), 0))(mirror_intermediate)
        )
    else:
        plate += translate((mirror_offset_x + 30, 0, -thick/2+rod_thick/2))(mirror_intermediate)

    plate += base()
    return plate


def crane_mirror_intermediate(rod_thick, arm_width, rod_to_mirror, assemble=True):
    """outer rod in y-dir, centered in xz"""

    plate_diam = 40-2*arm_width
    plate = cylinder(d=plate_diam, h=rod_thick, center=True)
    plate += rotate((90,0,0))(cylinder(d=rod_thick, h=40, center=True))  # outer rod for mounting into something
    plate -= cylinder(d = plate_diam-2*arm_width, h=2*rod_thick, center=True)

    clip = rotate((-90,0,90))(single_rod_clamp(arm_width))  # clip for rod in x-direction, open to +z; rod at 0,0
    clip_translate_z = rod_to_mirror-rod_thick/2
    clip = translate((plate_diam/2-arm_width/2, 0, clip_translate_z))(clip)
    clip_height = 10  # TODO: hardcoded here and in base()
    plate_top = rod_thick/2
    clip_bottom = rod_to_mirror-rod_thick/2 - clip_height/2
    clip_to_plate_gap = clip_bottom - plate_top
    if clip_to_plate_gap > 0:
        warnings.warn("Need to fill this gap!")

    plate += clip
    plate += mirror((1,0,0))(plate)

    mirror_plate_final = crane_mirror_final(plate_diam, rod_thick)

    if assemble:
        mirror_plate_final = translate((0, 0, rod_to_mirror-rod_thick/2))(mirror_plate_final)
    else:
        mirror_plate_final = rotate((180,0,0))(translate((40, 0, 0))(mirror_plate_final))  # rotate handle up

    return plate + mirror_plate_final


def crane_mirror_final(intermediate_diam, rod_thick):
    """rod in x-dir, centered in yz"""
    handle_length = 30

    plate_diam = intermediate_diam-2*rod_thick
    print("final plate diameter: {:.1f}mm".format(plate_diam))
    plate = cylinder(d=plate_diam, h=rod_thick, center=True)
    plate += rotate((0,90,0))(cylinder(d=rod_thick, h=intermediate_diam, center=True))  # outer rod for mounting into something

    plate += translate((0,0, -(handle_length-rod_thick)/2))(cylinder(d=rod_thick, h=handle_length, center=True))

    return plate



if __name__ == '__main__':

    _fine=True
    if _fine:
        header = "$fa = 5;"  # minimum face angle
        header += "$fs = 0.1;"  # minimum face size
    else:
        header = ""

    scad_render_to_file(crane_45deg_mirror(), "scad/crane_owis_45deg_mirror.scad", file_header=header)

    scad_render_to_file(crane_mirror(True), "scad/crane_mirror_assembled.scad", file_header=header)

    scad_render_to_file(crane_mirror(False), "scad/crane_mirror_printable.scad", file_header=header)
