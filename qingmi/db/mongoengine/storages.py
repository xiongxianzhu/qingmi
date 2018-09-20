# coding: utf-8
import os
import shutil
from flask import current_app


def is_empty_folder(folder):
    for root, dirs, files in os.walk(folder):
        if len(dirs) == 0 and len(files) == 0:
            return True
        return False


def load_file(name):
    if os.path.exists(name):
        with open(name) as fd:
            return fd.read()


def save_file(name, content):
    dirname = os.path.dirname(name)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(name, 'w+') as fd:
        fd.write(content)


def remove_file(name, path):
    if os.path.exists(name):
        os.remove(name)

        folder = os.path.dirname(name)
        while folder != path:
            if is_empty_folder(folder):
                shutil.rmtree(folder)
            folder = os.path.dirname(folder)
