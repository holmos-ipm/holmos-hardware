# -*- coding: utf-8 -*-
"""
Created on 08.01.2019

@author: beckmann
"""
from solid import scad_render_to_file

from Holmos import round_mount_light

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

    scad_render_to_file(round_mount_light(20, opening_angle=None, stop_inner_diam=19),
                        "scad/objective_mount_edmund4x_simple.scad", file_header=header)

    # with stop - lenses
    for d in (25.4,):
        scad_render_to_file(round_mount_light(d, opening_angle=None, stop_inner_diam=d-2),
                        "scad/lens mount_d{:.1f}.scad".format(d), file_header=header)

    # without stop - lasers
    for d in (12,):
        scad_render_to_file(round_mount_light(d, opening_angle=None), "scad/round_mount_d{:.1f}.scad".format(d), file_header=header)
