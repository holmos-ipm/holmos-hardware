import functools
import os


def safe_mkdir(*args):
    """ensure all directories exist, create them if neccessary.
    All non-existing intermediate directories are created."""
    for dir_path in args:
        if dir_path is not None:
            subdirs = split_path_full(dir_path)
            if subdirs[0][-1] == ":":
                subdirs[0] = subdirs[0]+"\\"
            print("subdirs:", subdirs)
            absolute_subdirs = [functools.reduce(os.path.join, subdirs[:i+1], "") for i in range(len(subdirs))]
            print(absolute_subdirs)
            for abs_dir in absolute_subdirs:
                if not os.path.exists(abs_dir):
                    os.mkdir(abs_dir)


def split_path_full(path):
    """
    Split a filesystem path into a list of its components
    os.path.split() only separates the last dir/file from a full path.
    """
    path = os.path.normpath(path)
    components = filter(lambda p: p is not "", path.split(os.sep))   # remove "" empty path from absolute linux paths
    return list(components)