# coding: utf-8

import os
import time
import hashlib


class BaseGenerator(object):

    def __init__(self, **kwargs):
        pass


class RandomGenerator(BaseGenerator):

    def __call__(self):
        md5_str = hashlib.md5(os.urandom(32)).hexdigest()
        return md5_str

