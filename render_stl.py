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
# library to fetch os information
import platform

# os_is can be 'windows', 'darwin' or 'linux'
os_is = platform.system().lower()
# uncommend below for troubleshouting
# print('the programm is runnuing on ' + os_is)


IDLE_PRIORITY_CLASS = 0x00000040

__config = configparser.ConfigParser()
__config.read("global_settings.ini")
# using f'string' format to create the right os path
path_to_openscad = __config.get("environ", f"{os_is}_path_to_openscad", fallback="not configured")


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
        
        if os_is == 'windows':  # windows path
            proc = subprocess.Popen(cmdline, creationflags=IDLE_PRIORITY_CLASS)
        else:                   # mac OS and linux path
            proc = subprocess.Popen(cmdline, shell=True)

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


def print_git_info_to_dir(path):
    info = get_git_info(path)
    if info is not None:
        with open(os.path.join(path, "version_info.txt"), "w+") as f:
            f.write(info)


def get_git_info(path='.'):
    try:
        import git
    except ModuleNotFoundError:
        print("git not found. Aborting.")
        return None
    repo = git.Repo(path, search_parent_directories=True)
    git_root = repo.git.rev_parse("--show-toplevel")

    info = "git info for ../{}:\n".format(os.path.split(git_root)[1])  # trailing folder name in path = repo name

    info += "Revision {}\n".format(repo.git.describe())

    changed_files = [item.a_path for item in repo.index.diff(None)]
    if len(changed_files) > 0:
        info += "...with changes to:\n"
    else:
        info += "...with no changed files.\n"
    for file in changed_files:
        info += "    {}\n".format(file)
    return info


if __name__ == '__main__':
    print(get_git_info())
