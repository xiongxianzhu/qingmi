# coding: utf-8
import re
import urllib
import json
from flask import current_app
from qingmi.utils import md5

__all__ = [
    'send_smsbao_sms'
]


def send_smsbao_sms(phone, text):
    """ 使用短信宝接口发送短信 """

    smsbao_settings = current_app.config.get('SMSBAO_SETTINGS')

    statusStr = {
        '0': '短信发送成功',
        '-1': '参数不全',
        '-2': '服务器空间不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间',
        '30': '密码错误',
        '40': '账号不存在',
        '41': '余额不足',
        '42': '账户已过期',
        '43': 'IP地址限制',
        '50': '内容含有敏感词'
    }

    smsapi = "http://api.smsbao.com/"
    # 短信平台账号
    user = smsbao_settings['user']
    # 短信平台密码
    password = md5(smsbao_settings['password'])

    data = dict(
        u=user,
        p=password,
        m=phone,
        c=text
    )

    url_values = urllib.parse.urlencode(data)
    send_url = smsapi + 'sms?' + url_values
    response = urllib.request.urlopen(send_url)
    the_page = response.read().decode('utf-8')

    res = dict(code=the_page, msg=statusStr[the_page])
    return res