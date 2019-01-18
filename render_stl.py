# -*- coding: utf-8 -*-
"""
Created on 09.01.2019

@author: beckmann

Renders all models in /scad to /stl
"""
import configparser
import os
import subprocess
import time


IDLE_PRIORITY_CLASS = 0x00000040

__config = configparser.ConfigParser()
__config.read("global_settings.ini")
path_to_openscad = __config.get("environ", "path_to_openscad", fallback="not configured")


def render_scad_dir_to_stl_dir(scad_dir, stl_dir):
    if not os.path.isfile(path_to_openscad):
        print("could not find openscad at {} - please install opensacd and edit the path in global_settings.ini".format(path_to_openscad))
        return
    files = filter(lambda f: ".scad" in f, os.listdir(scad_dir))
    processes = []
    for filename in list(files):
        filepath = os.path.join(scad_dir, filename)
        outfile = filename.replace(".scad", ".stl")
        outfile = os.path.join(stl_dir, outfile)
        print("rendering:", outfile)
        if os.path.isfile(outfile):
            os.remove(outfile)
            print(outfile, "deleted")
        cmdline = "{} -o \"{}\" \"{}\"".format(path_to_openscad, outfile, filepath)
        print(cmdline)
        proc = subprocess.Popen(cmdline, creationflags=IDLE_PRIORITY_CLASS)
        processes.append(proc)

    while True:
        num_running = 0
        for proc in processes:
            if proc.poll() is None:
                num_running += 1
        if num_running == 0:
            break
        print("waiting for {}/{} processes".format(num_running, len(processes)))
        time.sleep(1)

    print(processes[0].stderr)
