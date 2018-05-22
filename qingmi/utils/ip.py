# coding: utf-8
from flask import request


def get_ip():
    if 'Cdn-Real-Ip' in request.headers:
        return request.headers['Cdn-Real-Ip']
    if 'X-Real-Forwarded-For' in request.headers:
        return request.headers['X-Real-Forwarded-For'].split(',')[0]
    if 'X-FORWARDED-FOR' in request.headers:
        return request.headers['X-FORWARDED-FOR'].split(',')[0]
    return request.headers.get('X-Real-Ip') or request.remote_addr
