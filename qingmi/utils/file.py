# coding: utf-8
import os
import shutil
from qingmi._compat import to_bytes, urljoin


def check_empty_folder(folder):
    for root, dirs, files in os.walk(folder):
        if len(dirs) == 0 and len(files) == 0:
            return True
        return False

def read(dest):
    """Read content of a file."""
    if os.path.exists(dest):
        with open(dest) as f:
            return f.read()

def write(dest, body):
    """Write content to a file."""
    dirname = os.path.dirname(dest)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(dest, 'wb+') as f:
        f.write(to_bytes(body))

def delete(dest):
    """Delete the specified file."""
    if os.path.exists(dest):
        os.remove(dest)

def clean_up(dir_path):
    if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
