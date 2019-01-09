# -*- coding: utf-8 -*-
"""
Created on 09.01.2019

@author: beckmann

Renders all models in /scad to /stl
"""
import os
import subprocess
import time

files = filter(lambda f: ".scad" in f, os.listdir("scad"))
processes = []
IDLE_PRIORITY_CLASS = 0x00000040
for filename in list(files):
    filepath = os.path.join("scad", filename)
    outfile = filename.replace(".scad", ".stl")
    outfile = os.path.join("stl", outfile)
    print("rendering:", outfile)
    if os.path.isfile(outfile):
        os.remove(outfile)
        print(outfile, "deleted")
    cmdline = "C:\Program Files\OpenSCAD\openscad.exe -o \"{}\" \"{}\"".format(outfile, filepath)
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
