# coding: utf-8

import os
import time
import hashlib


class BaseGenerator(object):

    def __init__(self, local=False):
        self.local = local


class RandomGenerator(BaseGenerator):

    def __call__(self):
        md5 = hashlib.md5(os.urandom(32)).hexdigest()
        return md5

