# -*- coding: utf-8 -*-

from solid.utils import *  # pip install Solidpython
import numpy

from base import owis_holes, base, owis23hole
from helpers import cyl_arc, hexagon, rounded_plate


def round_mount_light(inner_diam=17.9, ring_thick=3, opening_angle=30, stop_inner_diam=None):
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
    z_thick = 10 # thickness/z-length of entire assembly
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
    ring = cyl_arc(r=outer_diam/2, h=z_thick, a0=opening_angle, a1=-opening_angle)
    if stop_inner_diam is None:
        ring -= cylinder(d=inner_diam, h=2*z_thick, center=True)
    else:
        ring -= cylinder(d=stop_inner_diam, h=2*z_thick, center=True)
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

    return base_plate + ring + connector


def rpi_cam_mount():
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

    return base_plate + plate


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
            hole = translate([x, y, 0])(owis23hole())
            rpi_plate -= hole
    return rpi_plate


def rpi_mount():
    """Mount for Raspberry Pi using four screws.
    Requires four cylindrical spacers.
    RPi is in (optical) XZ-plane.
    Plate is printed in (printer) XY plane
    https://www.raspberrypi.org/documentation/hardware/raspberrypi/mechanical/rpi_MECH_3bplus.pdf"""
    hole_sep_z = 58
    hole_sep_x = 49

    hole_diam = 2  # M2.3
    strut_width = 10
    strut_thick = 3

    hole_diagonal = (hole_sep_x**2 + hole_sep_z**2)**.5

    strut_angle_deg = numpy.rad2deg(numpy.arctan(hole_sep_x/hole_sep_z))  # angle < 45°

    diag_strut = rounded_plate((strut_width, hole_diagonal+strut_width, strut_thick), strut_width/2)
    for y in (hole_diagonal/2, -hole_diagonal/2):
        thread = cylinder(d=hole_diam, h=2*strut_thick, center=True)
        thread = hole()(thread)
        diag_strut += translate((0, y, 0))(thread)

    cross = rotate((0, 0, -strut_angle_deg))(diag_strut)
    cross += rotate((0, 0, strut_angle_deg))(diag_strut)
    cross = translate((0, 0, -strut_thick/2))(cross)  # to z=0...-thick,

    mount_strut = cube((hole_sep_x, strut_width, strut_thick), center=True)
    mount_strut = translate((0, 0, -strut_thick/2))(mount_strut)  # to z=0...-thick,
    mount_strut += rotate((-90,0,0))(translate((0,20,0))(base()))  # from optical-axis coords to our coords.
    cross += translate((0, hole_sep_z/2, 0))(mount_strut)
    cross += translate((0, -hole_sep_z/2, 0))(mount_strut)

    return cross


def slide_holder(display=True, angle_deg=0):
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

    if display:
        clamps = translate([1.3 * clamp_spacing / 2, 0, 0])(clamp)
        clamps += translate([-clamp_spacing / 2, 0, 0])(clamp)

    else:  # separate for printing
        clamps = translate([clamp_spacing / 2 + clamp_length + 5, -20 + clamp_width / 2, 0])(rotate([0, 0, -90])(clamp))
        clamps += translate([-clamp_spacing / 2 - clamp_length - 5, -20 + clamp_width / 2, 0])(
            rotate([0, 0, 90])(clamp))

    base_plate = translate((0, clamp_width-base_thick, 0))(base_plate)

    return base_plate + clamps


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

def base_plate():
    """base plate for cheap holmos setup"""
    
    """size"""
    w = 70
    l = 120
    h = 10
    
    """distances of m6 holes to fit 25 mm optical table"""    
    dx = 50
    dy = 100
                
    plate = rounded_plate([w,l,h], r=6)
    
    """m6 holes"""
    plate -= translate([-dx/2, -dy/2, h/2])(cylinder(d=12, center=True, h=10))
    plate -= translate([-dx/2, -dy/2, -h/2])(cylinder(d=6, center=True, h=15))
    
    plate -= translate([-dx/2, dy/2, h/2])(cylinder(d=12, center=True, h=10))
    plate -= translate([-dx/2, dy/2, -h/2])(cylinder(d=6, center=True, h=15))
    
    plate -= translate([dx/2, -dy/2, h/2])(cylinder(d=12, center=True, h=10))
    plate -= translate([dx/2, -dy/2, -h/2])(cylinder(d=6, center=True, h=15))
    
    plate -= translate([dx/2, dy/2, h/2])(cylinder(d=12, center=True, h=10))
    plate -= translate([dx/2, dy/2, -h/2])(cylinder(d=6, center=True, h=15))
    
    """actual cage system"""
    c_dx = 30
    c_dy = 60
    c_r  = 6
        
    plate += translate([-c_dx/2, -c_dy/2, h])(cylinder(d=12, center=True, h=20))
    plate -= translate([-c_dx/2, -c_dy/2, h])(cylinder(d=c_r, center=True, h=50))
    
    plate += translate([c_dx/2, -c_dy/2, h])(cylinder(d=12, center=True, h=20))
    plate -= translate([c_dx/2, -c_dy/2, h])(cylinder(d=c_r, center=True, h=50))
    
    plate += translate([-c_dx/2, c_dy/2-15, h])(cylinder(d=12, center=True, h=20))
    plate -= translate([-c_dx/2, c_dy/2-15, h])(cylinder(d=c_r, center=True, h=50))
    
    c_r  = 6.1
        
    plate += translate([-c_dx/2, -c_dy/2+15, h])(cylinder(d=12, center=True, h=20))
    plate -= translate([-c_dx/2, -c_dy/2+15, h])(cylinder(d=c_r, center=True, h=50))
    
    plate += translate([c_dx/2, -c_dy/2+15, h])(cylinder(d=12, center=True, h=20))
    plate -= translate([c_dx/2, -c_dy/2+15, h])(cylinder(d=c_r, center=True, h=50))
    
    plate += translate([-c_dx/2, c_dy/2, h])(cylinder(d=12, center=True, h=20))
    plate -= translate([-c_dx/2, c_dy/2, h])(cylinder(d=c_r, center=True, h=50))
    
    plate -= rotate([0,90,0])(translate([-c_dx/2, -c_dy/2, 15])(owis23hole()))
    plate -= rotate([0,-90,0])(translate([c_dx/2, -c_dy/2, 15])(owis23hole()))
    plate -= rotate([0,90,0])(translate([-c_dx/2, -c_dy/2-15, 15])(owis23hole()))
    
    plate -= rotate([0,90,0])(translate([-c_dx/2, -c_dy/2+15, 15])(owis23hole()))
    plate -= rotate([0,-90,0])(translate([c_dx/2, -c_dy/2+15, 15])(owis23hole()))
    plate -= rotate([0,90,0])(translate([-c_dx/2, c_dy/2, 15])(owis23hole()))
    
    return plate


def stabilizer_plate():
    """stabilizer plate for cheap holmos setup"""

    """size"""
    width = 40
    length = 65
    height = 10

    plate = rounded_plate([width,length,height], r=6)
    plate -= translate([width/4, length/3, 0])(rounded_plate([width,length,height+10], r=6))

    """actual cage system"""
    c_dx = 30
    c_dy = 60
    c_r = 6

    tube_length = 30

    tube_z_shift = (tube_length-height)/2

    tube = cylinder(d=12, center=True, h=tube_length)
    tube += hole()(cylinder(d=c_r, center=True, h=2*tube_length))
    tube += hole()(translate([-6.1, 0, tube_length/2-5])(rotate([0,90,0])(owis23hole())))
    tube += hole()(translate([6.1, 0, tube_length/2-5])(rotate([0,-90,0])(owis23hole())))

    for (dx, dy) in ((-c_dx/2, -c_dy/2),
                     (c_dx/2, -c_dy/2),
                     (-c_dx/2, c_dy/2-15)):
        for cr, ddy in ((6, 0), (6.1, 15)):
            final_y = dy+ddy
            plate += translate((dx, final_y, tube_z_shift))(tube)

    return plate


if __name__ == "__main__":
    import os
    import subprocess
    import time

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
    scad_render_to_file(slide_holder(False, 45), "scad/beamsplitter-holder.scad", file_header=header)

    #scad_render_to_file(round_mount_light(), "scad/Kosmos in Owis - offen.scad", file_header=header)

    scad_render_to_file(rpi_cam_mount(), "scad/RPi-Cam in Owis.scad", file_header=header)
    
    #scad_render_to_file(objective_mount(), "scad/Objective_Mount.scad", file_header=header)
    
    scad_render_to_file(base_plate(), "scad/Base_Plate.scad", file_header=header)

    scad_render_to_file(stabilizer_plate(), "scad/Stabilizer_Plate.scad", file_header=header)

    scad_render_to_file(rpi_mount(), "scad/rpi_mount.scad", file_header=header)


