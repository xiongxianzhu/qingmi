# coding: utf-8
from __future__ import unicode_literals

def success(_data, **kwargs):
    res = dict(code=0, key='SUCCESS')
    if _data is not None:
        res['data'] = _data
    elif kwargs:
        res['data'] = kwargs
    return res