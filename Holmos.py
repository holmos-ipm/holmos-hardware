# -*- coding: utf-8 -*-
"""
Created on 10.01.2019

@author: beckmann, bertz

Parts for Holmos holographic microscope.

All "final" functions - that is, parts that are supposed to be printed, need the keyword argument "assemble".
This way, the reference assembly and the bill of materials can be generated using the same functions.

If assemble=False, return the part so that it can be 3D-printed from z=0 upwards.
                   The printer bed is the xy-plane.
If assemble=True, return the part so that the optical axis is at z=0, with laser light traveling downwards
                  The table (or the RPi camera) is the xy plane
"""

from solid.utils import *  # pip install Solidpython
import numpy

from base import owis_holes, base, hole23, single_rod_clamp, base_rods30, rods30_dist_third_rod, rods30_diag_third_rod
from helpers import cyl_arc, hexagon, rounded_plate


def round_mount_light(inner_diam=17.9, ring_thick=3, opening_angle=30, stop_inner_diam=None, cyl_length=10, assemble=False):
    """
    mount for cylinder centered on optical axis (z). If opening_angle is None, clamping tabs are added.
    defaults: mount for Kosmos objective
    :param inner_diam: usually diameter of thing to be mounted
    :param ring_thick: thickness of ring determines stiffness
    :param opening_angle: ring is opened from -angle to +angle
    :param stop_inner_diam: if not None, a smaller second cylinder acts as a stop, i.e. for a lens.
    :return: Scad object
    """
    base_thick = 5
    connector_w = 3
    z_thick = 10  # thickness/z-length of entire assembly
    z_think_inner = 2

    do_clamp = False
    if opening_angle is None:
        do_clamp = True
        opening_angle = numpy.arcsin(ring_thick/inner_diam)
        opening_angle = numpy.rad2deg(opening_angle)

    base_plate = translate([0, -20 + base_thick / 2, 0])(
        rotate([90, 0, 0])(
            rounded_plate([30, 10, base_thick], 4)
        )
    )
    base_plate += base()

    outer_diam = inner_diam+2 * ring_thick
    ring = cyl_arc(r=outer_diam/2, h=cyl_length, a0=opening_angle, a1=-opening_angle)
    ring = translate((0,0, (cyl_length-z_thick)/2))(ring)
    if stop_inner_diam is None:
        ring -= cylinder(d=inner_diam, h=2*cyl_length, center=True)
    else:
        ring -= cylinder(d=stop_inner_diam, h=2*cyl_length, center=True)
        ring -= translate((0,0,z_think_inner))(cylinder(d=inner_diam, h=z_thick, center=True))

    if do_clamp:  # clamps with holes extending towards +x
        hex_diam = 5.5  # M3 nut
        clamp_extension = hex_diam + 1
        hole_diam = 3.5
        clamp_length = ring_thick+clamp_extension
        single_clamp = rounded_plate((clamp_length, z_thick, ring_thick), True)
        through_nut_hole = cylinder(d=hole_diam, h=2*ring_thick, center=True)
        through_nut_hole += translate((0,0, ring_thick/2))(hexagon(hex_diam, ring_thick/3))
        single_clamp -= translate([ring_thick/2, 0, 0])(through_nut_hole)
        ring += translate([inner_diam/2 + clamp_length/2, ring_thick, 0])(rotate([-90, 0, 0])(single_clamp))
        ring += translate([inner_diam/2 + clamp_length/2, -ring_thick, 0])(rotate([90, 0, 0])(single_clamp))

    connector_h = (40 - inner_diam) / 2
    connector_yc = inner_diam / 2 + connector_h / 2
    connector = translate([5, -connector_yc, 0])(cube([connector_w, connector_h, z_thick], center=True))
    connector += translate([-5, -connector_yc, 0])(cube([connector_w, connector_h, z_thick], center=True))

    label = "d = {:.1f}".format(inner_diam)
    info_text = linear_extrude(height=.5, center=True)(
                    text(label, valign="center", halign="center", size=3., segments=1,
                         font="Liberation Mono:style=Bold")
                )

    base_plate += translate((0, -(20-base_thick/2), z_thick/2))(info_text)

    mount = base_plate + ring + connector

    if assemble:
        mount = rotate((0, 180, 0))(mount)

    return mount


def rpi_cam_mount(assemble=False):
    # https://www.raspberrypi.org/documentation/hardware/camera/rpi-cam-v2_1-dimensions.pdf
    # 2016-11-30: printed; works. but: needs 4 spacers to keep the smd components on the back of the camera from touching the plate.
    rpi_thick = 3

    strut_y_end = 14.5
    struts_x = [-7.5, 7.5]
    strut_thick = 3

    base_thick = 5

    # base_plate = translate([0, -20+base_thick/2, 0])(cube([40, base_thick, 10], center=True))
    base_plate = translate([0, -20 + base_thick / 2, 0])(
        rotate([90, 0, 0])(
            rounded_plate([30, 10, base_thick], 2)
        )
    )
    base_plate += base()

    plate = translate([0, 0, -5])(rpi_cam_plate(rpi_thick))

    for strut_x in struts_x:
        strut = translate([strut_x, -(20 - strut_y_end) / 2, 0])(cube([strut_thick, 20 + strut_y_end, 10], center=True))
        cyl = rotate([0, 90, 0])(cylinder(r=10, h=50, center=True))  # cylinder along x-axis, in origin
        cyl = scale([1, (strut_y_end + 20 - base_thick) / 10, 1])(cyl)  # z=10, y = strut height
        cyl = translate([0, -20 + base_thick, -5])(cyl)  # axis into front top edge of base plate
        strut *= cyl
        plate += strut

    mount = base_plate + plate
    if assemble:
        mount = rotate((0, 180, 0))(mount)

    return mount


def rpi_cam_plate(thick=5):
    "plate for raspberry pi camera, with camera at [0,0,0], facing down"
    rpi_holes_x_2 = 21 / 2
    rpi_holes_y = 12.5
    rpi_border = 2
    rpi_plate = translate([0, rpi_holes_y / 2, thick / 2])(  # one pair of holes (and camera) are at y=0
        rounded_plate([2 * rpi_holes_x_2 + 2 * rpi_border, rpi_holes_y + 2 * rpi_border, thick], rpi_border)
    )
    for x in [rpi_holes_x_2, -rpi_holes_x_2]:
        for y in [0, rpi_holes_y]:
            hole = translate([x, y, 0])(hole23())
            rpi_plate -= hole
    return rpi_plate


def rpi_mount(assemble=False):
    """Mount for Raspberry Pi using four screws.
    Requires four cylindrical spacers.
    RPi is in (optical) XZ-plane.
    Plate is printed in (printer) XY plane
    https://www.raspberrypi.org/documentation/hardware/raspberrypi/mechanical/rpi_MECH_3bplus.pdf"""
    hole_sep_z = 58
    hole_sep_x = 49

    strut_width = 10
    strut_thick = 3

    hole_diagonal = (hole_sep_x**2 + hole_sep_z**2)**.5

    strut_angle_deg = numpy.rad2deg(numpy.arctan(hole_sep_x/hole_sep_z))  # angle < 45°

    diag_strut = strut_with_holes(hole_diagonal, strut_thick, strut_width)

    cross = rotate((0, 0, -strut_angle_deg))(diag_strut)
    cross += rotate((0, 0, strut_angle_deg))(diag_strut)
    cross = translate((0, 0, -strut_thick/2))(cross)  # to z=0...-thick,

    mount_strut = cube((hole_sep_x, strut_width, strut_thick), center=True)
    mount_strut = translate((0, 0, -strut_thick/2))(mount_strut)  # to z=0...-thick,
    baseplate = base(rod_sep=rods30_diag_third_rod)  # works for threads20 as well: superfluous kwargs are ignored.
    mount_strut += rotate((-90, 0, 0))(translate((0, 20, 0))(baseplate))  # from optical-axis coords to our coords.
    cross += translate((0, hole_sep_z/2, 0))(mount_strut)
    cross += translate((0, -hole_sep_z/2, 0))(mount_strut)

    if assemble:
        cross = translate((20, -rods30_diag_third_rod/2-25, 0))(rotate((90, 0, -90))(cross))

    return cross


def strut_with_holes(hole_dist, strut_thick, strut_width):
    """flat strut with two holes at y=+-hole_dist"""
    diag_strut = rounded_plate((strut_width, hole_dist + strut_width, strut_thick), strut_width / 2)
    for y in (hole_dist / 2, -hole_dist / 2):
        thread = hole23(length=50)
        thread = hole()(thread)
        diag_strut += translate((0, y, -strut_thick / 2))(thread)
    return diag_strut


def slide_holder(assemble=True, angle_deg=0):
    """deg=0: "normal" orientation: slide is perpendicular to optical axis"""
    dov_h = 3
    dov_w0 = 5
    dov_w1 = 7
    dov_pad = .1

    base_thick = 5
    clamp_width = 8
    clamp_spacing = 40 - clamp_width
    clamp_base = 2
    clamp_reach = 20 - base_thick - clamp_base
    clamp_length = numpy.sqrt(2) * clamp_reach

    base_plate = translate([0, -(40 - base_thick) / 2, 0])(cube([40, base_thick, 10], center=True))
    base_plate += base()
    base_plate = rotate((0, angle_deg, 0))(base_plate)

    base_plate += translate([0, -(40 - base_thick) / 2, 0])(cube([40, base_thick, 10], center=True))

    clamp = translate([0, 0, -1])(slide_clamp(clamp_reach, clamp_length, base_height=clamp_base, width=clamp_width))

    # dovetail: parts touch at y=0, tail into -y
    trap_pts = [[dov_w0 / 2, 0], [-dov_w0 / 2, 0], [-dov_w1 / 2, -dov_h], [dov_w1 / 2, -dov_h]]
    trap_pts_padded = [[dov_w0 / 2 + dov_pad, .01], [-dov_w0 / 2 - dov_pad, .01],
                       [-dov_w1 / 2 - dov_pad, -dov_h - dov_pad], [dov_w1 / 2 + dov_pad, -dov_h - dov_pad]]
    trap_clear = [[dov_w0 / 4, -dov_h / 2], [-dov_w0 / 4, -dov_h / 2], [-dov_w1 / 4, -1.01 * dov_h],
                  [dov_w1 / 4, -1.01 * dov_h]]
    dov_section = polygon(trap_pts) - polygon(trap_clear)
    dov_section_pad = polygon(trap_pts_padded)

    dov = linear_extrude(height=clamp_width)(dov_section)
    dov_pad = linear_extrude(height=2 * clamp_width)(dov_section_pad)

    dov = rotate([0, 90, 0])(
        translate([0, 0, -clamp_width / 2])(dov)
    )
    clamp += translate([0, -clamp_reach - clamp_base, 0])(dov)

    dov_pad = rotate([0, 90, 0])(
        translate([0, 0, -clamp_width])(dov_pad)
    )
    base_plate -= translate([20, -clamp_reach - clamp_base, 0])(dov_pad)
    base_plate -= translate([-20, -clamp_reach - clamp_base, 0])(dov_pad)

    if assemble:
        clamps = translate([1.3 * clamp_spacing / 2, 0, 0])(clamp)
        clamps += translate([-clamp_spacing / 2, 0, 0])(clamp)
        base_plate += cylinder(d=1, h=1, center=True)  # visualize optical axis
        assembly = rotate((0, -angle_deg, 0))(base_plate + clamps)

    else:  # separate for printing
        clamp = translate([7, 40, (clamp_width-10)/2])(rotate((0,90,0))(clamp))
        clamps = clamp + mirror((1, 0, 0))(clamp)
        base_plate = rotate((-90, 0, 0))(translate((0, 20, 0))(base_plate))
        assembly = base_plate + clamps

    return assembly


def slide_clamp(clamping_reach, clamp_length, base_height=5, width=8):
    # single clamp to clamp a glass slide to the z=0 plane, open from +y
    gap_width = 0.5  # Kosmos glass: 1 mm
    back_thick = 4
    clip_thick = 1.5
    clip_wave = 4

    total_height = clamp_length + base_height
    clip_z_extent = clip_thick + clip_wave + gap_width
    total_thick = back_thick + clip_z_extent

    clip_ys = numpy.linspace(clamp_length - clamping_reach, -clamping_reach, 50)
    clip_xs = gap_width + clip_wave / 2 - clip_wave / 2 * numpy.cos(clip_ys / clamping_reach * numpy.pi)
    clip_ys = numpy.hstack([clip_ys, clip_ys[::-1]])
    clip_xs = numpy.hstack([clip_xs + clip_thick, clip_xs[::-1]])
    clip = polygon(list(zip(clip_xs, clip_ys)))
    clip = linear_extrude(height=width)(clip)
    clip = translate([width / 2, 0, 0])(rotate([0, -90, 0])(clip))

    back = translate([0, -total_height / 2 + (clamp_length - clamping_reach), -back_thick / 2])(
        cube([width, total_height, back_thick], center=True))
    base = translate([0, -clamping_reach - base_height / 2, (clip_z_extent - back_thick) / 2])(
        cube([width, base_height, back_thick + clip_z_extent], center=True))

    return clip + back + base


def objective_mount():
    """mount for microscope objective"""
    
    mount = rounded_plate([40, 40, 10], r=5)
    mount -= owis_holes(True)
    mount -= cylinder(d=20, center=True, h=11)
    
    return mount


def tube_with_rodmount():
    """base_plate with 3 clamps for new HolMOS-Cage"""
    
    mount = base_rods30(z_length=30)
    mount += translate((0,0,-15))(cylinder(d=43, h=30))
    mount += translate((0,-10,0))(cube((40,20,30), center=True))
    mount -= translate((0,0,-30))(cylinder(d=38, h=60))
    
    return mount


def cage_stabilizer(assemble=False):
    """stabilizer with 3 clamps for new HolMOS-Cage"""
    
    cage_base = 30
    stabilizer_base = rods30_dist_third_rod
    stabilizer_height = 10
    
    angle = -atan(cage_base/2/stabilizer_base)/math.pi*180 
     
    stabilizer = translate((0,stabilizer_base/2,0))(cube((cage_base+4,stabilizer_base-10,stabilizer_height), center=True))
    
    stabilizer -= translate((-cage_base,stabilizer_base/2,0))(rotate((0,0,angle))(cube((cage_base,stabilizer_base,2*stabilizer_height), center=True)))
    stabilizer -= translate((cage_base,stabilizer_base/2,0))(rotate((0,0,-angle))(cube((cage_base,stabilizer_base,2*stabilizer_height), center=True)))
    
    for (dd,y) in ((20,20),(10,40)):
        stabilizer -= translate((0,y,0))(cylinder(d=dd, h=20, center=True))
               
    mount_strut = translate((0,25,0))(base() )
    mount_strut += translate((0,60,0))(rotate((0,0,180))(single_rod_clamp()))
    
    stabilizer += mount_strut

    stabilizer = translate((0, -25, 0))(mirror((0, 1, 0))(stabilizer))
    
    return stabilizer


def cage_side_stabilizer():
    """stabilizer for both sides of new HolMOS-Cage"""
    
    sep_z = 100
    sep_x = rods30_diag_third_rod

    strut_width = 10
    strut_thick = 3

    diagonal = (sep_x**2 + sep_z**2)**.5

    strut_angle_deg = numpy.rad2deg(numpy.arctan(sep_x/sep_z))  # angle < 45°

    diag_strut = rounded_plate((strut_width, diagonal+strut_width, strut_thick), strut_width/2)
    
    cross = rotate((0, 0, -strut_angle_deg))(diag_strut)
    cross += rotate((0, 0, strut_angle_deg))(diag_strut)

    cross = translate((0, 0, -strut_thick/2))(cross)  # to z=0...-thick,

    mount_strut = cube((sep_x, strut_width, strut_thick), center=True)
    mount_strut = translate((0, 0, -strut_thick/2))(mount_strut)  # to z=0...-thick,
    mount_strut += rotate((-90,0,0))(translate((0,20,0))(base_rods30(rod_sep=sep_x)))  # from optical-axis coords to our coords.
    cross += translate((0, sep_z/2, 0))(mount_strut)
    cross += translate((0, -sep_z/2, 0))(mount_strut)

    return cross


def cage_base_plate(assemble=False):
    """base_plate with 3 clamps for new HolMOS-Cage"""
    
    cage_base = 30
    stabilizer_base = 60
    stabilizer_height = 10
    
    angle = -atan(cage_base/2/stabilizer_base)/math.pi*180 
     
    plate = translate((0, stabilizer_base/2, 0))(cube((cage_base+4, stabilizer_base-10, stabilizer_height), center=True))
    
    plate -= translate((-cage_base, stabilizer_base/2, 0))(rotate((0, 0, angle))(cube((cage_base, stabilizer_base, 2*stabilizer_height), center=True)))
    plate -= translate((cage_base, stabilizer_base/2, 0))(rotate((0, 0, -angle))(cube((cage_base, stabilizer_base, 2*stabilizer_height), center=True)))
    
    for y in (15, 40):
        plate += hole()(translate([0, y, 5])(cylinder(d=12, center=True, h=10)))
        plate += hole()(translate([0, y, -5])(cylinder(d=7.5, center=True, h=2*10)))
               
    mount_strut = translate((0, 25, 10))(base_rods30(z_length=30))
    mount_strut += translate((0, 60, 10))(rotate((0, 0, 180))(single_rod_clamp(z_length=30)))

    for y in (10, stabilizer_base-5):
        strut_thick = 3
        strut = strut_with_holes(hole_dist=40, strut_thick=strut_thick, strut_width=10)
        plate += translate((0, y, (strut_thick-10)/2))(rotate((0, 0, 90))(strut))
    
    plate += mount_strut

    plate = translate((0, -25, 0))(mirror((0, 1, 0))(plate))
    
    return plate


if __name__ == "__main__":
    import os

    _fine = True
    render_STL = False

    if _fine:
        header = "$fa = 5;"  # minimum face angle
        header += "$fs = 0.1;"  # minimum face size
    else:
        header = ""

    if not os.path.exists("scad"):
        os.mkdir("scad")

    if not os.path.exists("stl"):
        os.mkdir("stl")

    scad_render_to_file(slide_holder(False), "scad/slide-holder.scad", file_header=header)
    scad_render_to_file(slide_holder(True), "scad/slide-holder-assembled.scad", file_header=header)
    scad_render_to_file(slide_holder(False, 45), "scad/beamsplitter-holder.scad", file_header=header)

    scad_render_to_file(rpi_cam_mount(), "scad/RPi-Cam.scad", file_header=header)

    scad_render_to_file(cage_stabilizer(), "scad/Cage_Stabilizer.scad", file_header=header)
    
    scad_render_to_file(cage_side_stabilizer(), "scad/Cage_Side_Stabilizer.scad", file_header=header)
    
    scad_render_to_file(cage_base_plate(), "scad/Cage_Base_Plate.scad", file_header=header)
    
    scad_render_to_file(tube_with_rodmount(), "scad/Tube_with_Rodmount.scad", file_header=header)

    scad_render_to_file(rpi_mount(), "scad/rpi_mount.scad", file_header=header)


    #render_scad_dir_to_stl_dir("scad", "stl")



