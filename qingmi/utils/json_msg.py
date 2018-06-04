# coding: utf-8
from flask import jsonify


def success(_data=None, code=0, msg='SUCCESS', **kwargs):
    # if kwargs.get('__external'):
    #     kwargs.setdefault('code', 0)
    #     kwargs.setdefault('key', 'SUCCESS')
    res = dict(code=code, msg=msg)
    if _data is not None:
        res['data'] = _data
    elif kwargs:
        res['data'] = kwargs
    return res

def error(_data=None, code=-1, msg='ERROR', **kwargs):
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
