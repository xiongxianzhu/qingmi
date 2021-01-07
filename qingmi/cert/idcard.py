# coding: utf-8

""" 身份证实名认证 """
import sys
import urllib.request
import json


def idcardcert(appcode, card_no):
    """ 身份证实名认证身份证二要素一致性验证 """
    host = 'http://idquery.market.alicloudapi.com'
    path = '/idcard/query'
    # method = 'GET'
    appcode = appcode
    querys = 'number=%s' % card_no
    # bodys = {}
    url = host + path + '?' + querys
    try:
        request = urllib.request.Request(url)
        request.add_header('Authorization', 'APPCODE ' + appcode)
        response = urllib.request.urlopen(request)
        content = response.read()
        if content:
            return json.loads(content.decode("unicode-escape"))
        return content
    except BaseException:
        return None
