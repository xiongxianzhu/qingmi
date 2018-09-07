# coding: utf-8

def is_wechat():
    ua = request.headers['User-Agent'].lower()
    return 'micromessenger' in ua

