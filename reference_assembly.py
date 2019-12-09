# -*- coding: utf-8 -*-
"""
Created on 16.01.2019

@author: beckmann

Demo of how all parts go together.
Generates SCAD files, and (if Openscad is found) compiles them to STL.

The STL files are added by manually copying ./stl/reference_assembly to ./
This way, they are not accidentally updated; the compiled STL files should only be updated on milestones, keeping the
git repository small.
"""
import os

from solid import *

import Holmos
import cage
import round_mounts
import mirror_mount
from file_tools import safe_mkdir
from render_stl import render_scad_dir_to_stl_dir, print_git_info_to_dir


class HolmosComponent:
    def __init__(self, z, part_func, name=None, **kwargs):
        self.part_func = part_func
        self.z = z
        self.name = name
        self.kwargs = kwargs  # keyword arguments for part_func


mount_bottom = False  # mount at bottom (screw into something) or top (hang from something)
h = 600
z0 = 30

part_list = [
             HolmosComponent(-z0, cage.cage_circumference),
             HolmosComponent(0, Holmos.rpi_cam_mount),
             HolmosComponent(50, cage.rpi_mount),
             HolmosComponent(185, round_mounts.round_mount_light,
                             inner_diam=20, opening_angle=None, stop_inner_diam=19, clip_length=20,
                             name="objective_lens_mount"),
             HolmosComponent(216, Holmos.slide_holder),
             HolmosComponent(252, Holmos.slide_holder, angle_deg=45,
                             name="beamsplitter_mount"),
             HolmosComponent(275, mirror_mount.crane_mirror),
             HolmosComponent(306, round_mounts.round_mount_light, inner_diam=25.4, opening_angle=None,
                             stop_inner_diam=23.4,
                             name="condensor_lens_mount"),
             HolmosComponent(500, cage.board_hook, name="board_hook"),
             HolmosComponent(550, round_mounts.round_mount_light, inner_diam=12, opening_angle=None,
                             name="laser_mount"),
             HolmosComponent(h-z0, cage.cage_circumference),
             ]


def holmos_full_assembly():
    assembly = translate((15, -25, h/2))(cylinder(d=6, h=h, center=True))
    for component in part_list:
        print("adding {}".format(component.name))
        this_part = component.part_func(assemble=True, **component.kwargs)
        assembly += translate((0, 0, z0+component.z))(this_part)
    return assembly


if __name__ == '__main__':

    _fine = True
    if _fine:
        header = "$fa = 5;"  # minimum face angle
        header += "$fs = 0.1;"  # minimum face size
    else:
        header = ""

    scad_path = "scad/reference_assembly"
    stl_path = "stl/reference_assembly"
    safe_mkdir(scad_path, stl_path)

    scad_render_to_file(holmos_full_assembly(), "scad/reference_assembly.scad", file_header=header)

    print("cleaning output dirs...")
    for file in os.listdir(scad_path):
        os.remove(os.path.join(scad_path, file))
    for file in os.listdir(stl_path):
        os.remove(os.path.join(stl_path, file))

    for number, part in enumerate(part_list):
        name_for_fn = part.name
        if name_for_fn is None:
            name_for_fn = part.part_func.__name__
        filename = "{:02d} - {}.scad".format(number, name_for_fn)
        print(filename)
        part_scad = part.part_func(assemble=False, **part.kwargs)
        scad_render_to_file(part_scad, os.path.join(scad_path, filename), file_header=header)

    print_git_info_to_dir(stl_path)
    render_scad_dir_to_stl_dir(scad_path, stl_path)
