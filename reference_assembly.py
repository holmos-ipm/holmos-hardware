# -*- coding: utf-8 -*-
"""
Created on 16.01.2019

@author: beckmann

Demo of how all parts go together
"""
import os

from solid import *
import Holmos
import lens_mounts
import mirror_mount
import base


class HolmosComponent:
    part = None
    z_above_cam = None
    print_to_optical_axis_func = None

    def __init__(self, part, z, func=None):
        self.part = part
        self.z = z

        if func is None:
            func = lambda p: p
        self.print_to_optical_axis_func = func


part_list = (HolmosComponent(Holmos.cage_base_plate(), -35),
             HolmosComponent(Holmos.rpi_mount(), 50,
                             lambda p: translate((20, -base.rods30_diag_third_rod/2-25, 0))(rotate((90, 0, -90))(p))),
             HolmosComponent(Holmos.rpi_cam_mount(), 0, rotate((0, 180, 0))),
             HolmosComponent(lens_mounts.round_mount_light(20, opening_angle=None, stop_inner_diam=19),
                                     185, rotate((0, 180, 0))),
             HolmosComponent(Holmos.slide_holder(True), 216),
             HolmosComponent(Holmos.slide_holder(True, 45), 252),
             HolmosComponent(mirror_mount.crane_mirror(True), 275, rotate((0, 180, 0))),
             HolmosComponent(lens_mounts.round_mount_light(25.4, opening_angle=None, stop_inner_diam=23.4), 306),
             HolmosComponent(Holmos.cage_stabilizer(), 500),
             HolmosComponent(lens_mounts.round_mount_light(12, opening_angle=None), 550)
             )


def holmos_full_assembly():
    z0 = 30
    h = 600

    assembly = translate((15, -25, h/2))(cylinder(d=6, h=h, center=True))
    for component in part_list:
        this_part = component.print_to_optical_axis_func(component.part)
        assembly += translate((0, 0, z0+component.z))(this_part)
    return assembly


if __name__ == '__main__':

    _fine = True
    if _fine:
        header = "$fa = 5;"  # minimum face angle
        header += "$fs = 0.1;"  # minimum face size
    else:
        header = ""

    if not os.path.exists("scad"):
        os.mkdir("scad")

    scad_render_to_file(holmos_full_assembly(), "scad/full_assembly.scad", file_header=header)

    if not os.path.exists("scad/ref"):
        os.mkdir("scad/ref")

    print("cleaning output dir...")
    for file in os.listdir("scad/ref"):
        os.remove(os.path.join("scad/ref", file))

    for part in part_list:
        scad_render_to_file(part.part)
