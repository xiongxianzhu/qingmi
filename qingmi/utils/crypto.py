# coding: utf-8
"""
Qingmi's standard crypto functions and utilities.
"""

import hashlib
import hmac
import random
import time
import base64


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """ 生成随机的字符串， 默认长度12个字符 """
    return ''.join(random.choice(allowed_chars) for i in range(length))


def get_random_secret_key():
    """ 生成一个50个字符组成的随机字符串作为SECRET_KEY的setting值 """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)


def get_phone_verify_code(length=4):
    """ 生成手机短信验证码 """
    chars = '0123456789'
    return get_random_string(length, chars)


def get_email_verify_code(length=4):
    """ 生成邮箱验证码 """
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' \
            + '0123456789'
    return get_random_string(length, chars)

def get_session_id(length=48):
    """ 生成session　id字符串 """
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' \
            + '0123456789-_'
    return get_random_string(length, chars)

def get_invite_code(length=6):
    """ 生成邀请码 """
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return get_random_string(length, chars)

def md5(data):
    """ md5算法加密字符串 """
    m = hashlib.md5()
    m.update(data.encode('utf-8'))
    return m.hexdigest()

def b64(data):
    """ base64算法编码字符串 """
    base64_encrypt = base64.b64encode(data.encode('utf-8'))
    return str(base64_encrypt, 'utf-8')

def base64_md5(data):
    """ 进行MD5加密，然后Base64编码 """
    return b64(md5(data))
