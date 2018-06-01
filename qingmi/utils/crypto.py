# coding: utf-8
"""
Qingmi's standard crypto functions and utilities.
"""

import hashlib
import hmac
import random
import time


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """ 生成随机的字符串， 默认长度12个字符 """
    return ''.join(random.choice(allowed_chars) for i in range(length))


def get_random_secret_key():
    """ 生成一个50个字符组成的随机字符串作为SECRET_KEY的setting值 """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)
