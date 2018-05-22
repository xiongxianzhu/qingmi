# coding: utf-8
from flask import jsonify


def success(code=0, msg='SUCCESS', _data=None, **kwargs):
    res = dict(code=code, msg=msg)
    if _data is not None:
        res['data'] = _data
    elif kwargs:
        res['data'] = kwargs
    return res

def error(code=-1, msg='ERROR', _data=None, **kwargs):
    res = dict(code=code, msg=msg)
    if _data is not None:
        res['data'] = _data
    elif kwargs:
        res['data'] = kwargs
    return res

def json_success(code=0, msg='SUCCESS', **kwargs):
    kwargs['code'] = code
    kwargs['msg'] = msg
    return jsonify(kwargs)

def json_error(code=-1, msg='ERROR', **kwargs):
    kwargs['code'] = code
    kwargs['msg'] = msg
    return jsonify(kwargs)
