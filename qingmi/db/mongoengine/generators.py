# coding: utf-8

import os
import time
import hashlib


class BaseGenerator(object):

    def __init__(self, local=False):
        self.local = local


class RandomGenerator(BaseGenerator):

    def __call__(self):
        random_md5_str = hashlib.md5(os.urandom(32)).hexdigest()
        return random_md5_str

