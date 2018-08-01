# -*- coding: utf-8 -*-

from solid.utils import *  # pip install Solidpython
import numpy


def owis_block():
    plate = cube([40, 40, 10], True)

    plate -= translate([0, -20, 0])(
        rotate([-90, 0, 0])(
            owis_holes()
        )
    )

    return plate


def owis_holes(move_to_minus_y=False):
    hole = owis23hole()
    owis_holes = translate([-10, 0, 0])(hole) + translate([10, 0, 0])(hole)  # z=0 is outside plane

    if move_to_minus_y:
        owis_holes = translate([0, -20, 0])(
            rotate([-90, 0, 0])(
                owis_holes
            )
        )
    return owis_holes


def owis23hole():
    "hole from below into z=0 plane"
    hole = cylinder(1, h=10, center=True)
    hole += translate([0, 0, -5])(
        cylinder(r1=2, r2=1, h=2, center=True)
    )
    return translate([0, 0, 5])(hole)


def kosmos_objective():
    plate = owis_block()

    # hole for clamping; slit plane is at z=0
    clamp_hole_4 = cylinder(d=3.3, h=30, center=True)  # self-cutting thread
    clamp_hole_4 += translate([0, 0, 10])(cylinder(d=4.5, h=20, center=True))  # through hole
    clamp_hole_4 += translate([0, 0, 20 - 2])(cylinder(d=7.5, h=4.1, center=True))  # head

    plate -= cylinder(d=17.9, h=20, center=True)

    plate -= translate([0, 20, 0])(cube([1, 40, 40], center=True))

    plate -= translate([0, 15, 0])(rotate([0, 90, 0])(clamp_hole_4))

    # Save weight:
    plate -= translate([-4, -15, 0])(cylinder(d=4, h=20, center=True))
    plate -= translate([4, -15, 0])(cylinder(d=4, h=20, center=True))
    plate -= translate([0, -15, 0])(cube([8, 4, 20], center=True))
    plate -= translate([0, -20, 0])(cube([12., 10, 20], center=True))

    plate -= translate([-20, 0, 0])(cube([10, 60, 20], center=True))
    plate -= translate([20, 0, 0])(cube([10, 60, 20], center=True))

    return plate


def kosmos_objective_open():
    base_thick = 5
    objective_diam = 17.9
    ring_thick = 3
    opening_diam = 15
    connector_w = 3

    base_plate = translate([0, -20 + base_thick / 2, 0])(
        rotate([90, 0, 0])(
            rounded_plate([30, 10, base_thick], 4)
        )
    )
    base_plate -= hole()(owis_holes(True))

    ring = cylinder(d=objective_diam + 2 * ring_thick, h=10, center=True)
    ring -= cylinder(d=objective_diam, h=20, center=True)
    ring -= translate([objective_diam / 2 + ring_thick, 0, 0])(cylinder(d=opening_diam, h=20, center=True))

    connector_h = (40 - objective_diam) / 2
    connector_yc = objective_diam / 2 + connector_h / 2
    connector = translate([5, -connector_yc, 0])(cube([connector_w, connector_h, 10], center=True))
    connector += translate([-5, -connector_yc, 0])(cube([connector_w, connector_h, 10], center=True))

    return base_plate + ring + connector


def rpi_cam_owis():
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
            rounded_plate([40, 10, base_thick], 2)
        )
    )
    base_plate -= hole()(owis_holes(True))

    plate = translate([0, 0, -5])(rpi_plate(rpi_thick))

    for strut_x in struts_x:
        strut = translate([strut_x, -(20 - strut_y_end) / 2, 0])(cube([strut_thick, 20 + strut_y_end, 10], center=True))
        cyl = rotate([0, 90, 0])(cylinder(r=10, h=50, center=True))  # cylinder along x-axis, in origin
        cyl = scale([1, (strut_y_end + 20 - base_thick) / 10, 1])(cyl)  # z=10, y = strut height
        cyl = translate([0, -20 + base_thick, -5])(cyl)  # axis into front top edge of base plate
        strut *= cyl
        plate += strut

    return base_plate + plate


def rpi_plate(thick=5):
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


def owis_slide_holder(display=True):
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
    base_plate -= hole()(owis_holes(True))

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

    scad_render_to_file(owis_slide_holder(False), "scad/Owis-slide-holder.scad", file_header=header)

    scad_render_to_file(kosmos_objective_open(), "scad/Kosmos in Owis - offen.scad", file_header=header)

    scad_render_to_file(kosmos_objective(), "scad/Kosmos-Objektiv in Owis.scad", file_header=header)

    scad_render_to_file(rpi_cam_owis(), "scad/RPi-Cam in Owis.scad", file_header=header)
