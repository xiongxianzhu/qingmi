# coding: utf-8
import hashlib

def md5(str):
    """ md5算法加密字符串 """
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()