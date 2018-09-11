# coding: utf-8
from flask import request

def is_wechat():
    ua = request.headers['User-Agent'].lower()
    return 'micromessenger' in ua


def get_useragent():
    """ 获取request的useragent """
    return request.headers.get('User-Agent')

