# -*- coding: utf-8 -*-
"""
Created on 10.01.2019

@author: beckmann
"""
import itertools
import numpy

from solid import *

from base import base, owis23hole
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
        thread = hole()(rotate((0, 180, 0))(owis23hole()))  # from above into z=0
        mirror_plate_threads += translate((x*screw_dist_from_center, y*screw_dist_from_center, thick/2))(thread)

    mirror_plate_threads = rotate((0, mirror_angle_deg, 0))(mirror_plate_threads)
    mirror_plate_threads = translate((0, 0, 40*numpy.tan(numpy.deg2rad(-mirror_angle_deg))))(mirror_plate_threads)

    plate += translate((mirror_offset, 0, 0))(mirror_plate_blank)
    plate += translate((mirror_offset, 0, 0))(mirror_plate_threads)

    plate += base()

    return plate


if __name__ == '__main__':

    scad_render_to_file(crane_45deg_mirror(), "scad/crane_owis_45deg_mirror.scad")
