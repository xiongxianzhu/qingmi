from flask import request


def is_wechat():
    if request:
        ua = request.headers['User-Agent'].lower()
        return 'micromessenger' in ua
    return False


def get_useragent():
    """ 获取request的useragent """
    if request:
        return request.headers.get('User-Agent')
    return None


def get_ip():
    if request:
        if 'Cdn-Real-Ip' in request.headers:
            return request.headers['Cdn-Real-Ip']
        if 'X-Real-Forwarded-For' in request.headers:
            return request.headers['X-Real-Forwarded-For'].split(',')[0]
        if 'X-FORWARDED-FOR' in request.headers:
            return request.headers['X-FORWARDED-FOR'].split(',')[0]
        return request.headers.get('X-Real-Ip') or request.remote_addr
    return None
