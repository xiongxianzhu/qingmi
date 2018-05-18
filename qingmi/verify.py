# coding: utf-8

import os
import random
import string
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from flask import current_app, session, request, make_response
from wheezy.captcha import image
from .settings import FONT_ROOT

__all__ = [

]

FONTS = [
    os.path.join(FONT_ROOT, '1.ttf'),
    os.path.join(FONT_ROOT, '2.ttf'),
    os.path.join(FONT_ROOT, '3.ttf'),
    os.path.join(FONT_ROOT, '4.ttf'),
]

BG_COLORS = ['#ffffff', '#fbfbfb', '#fdfeff']
TEXT_COLORS = ['#39f', '#3f9', '#93f', '#9f3', '#f93', '#f39']

SESSION_KEY_VERIFY = 'verify_codes'
_keys = set()

# 'A-Z0-9'
_chars = string.uppercase + string.digits
# 去掉干扰的字母和数字
# _chars = 'ABCDEFJHJKLMNPQRSTUVWXY3456789'
for char in '0oIl1Z2':
    _chars = _chars.replace(char, '')


class VerifyManager(object):

    def __init__(self, app=None, code_url='/verify-code'):
        self.code_url = code_url
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        @app.route(self.code_url)
        def verify_code():
            key = request.args.get('key', None)
            code, times = get_verify_code(key, refresh=True)
            return code2image(code)


def get_varify_code(key, refresh=False, code_len=4):
    """ 生成验证码字符串 """

    _keys.add(key)
    if SESSION_KEY_VERIFY not in session:
        session[SESSION_KEY_VERIFY] = dict()

    # 默认随机抽取4位字符生成验证码
    code = ''.join(random.sample(_chars, code_len))
    codes = session[SESSION_KEY_VERIFY]
    if key not in codes or refresh:
        # 将新生成的随机验证码和使用次数根据key添加到session
        codes[key] = dict(
            code=code,
            times=0
        )
    
    return codes[key]['code'], code[key]['times']

def code2image(code):
    """ 将验证码生成验证码图片 """

    captcha_image = image.captcha(drawings=[
        background(),
        text(fonts=FONTS,
            drawings=[
                image.warp(),
                image.rotate(),
                image.offset()
            ]),
        image.curve(),
        image.noise(),
        image.smooth()
    ])
    
    image = captcha_image(code)
    out = StringIO()
    image.save(out, "jpeg", quality=75)
    response = make_response(out.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

def validate_code(key):
    """ 检验验证码 """

    if SESSION_KEY_VERIFY not in session:
        session[SESSION_KEY_VERIFY] = dict()

    codes = session[SESSION_KEY_VERIFY]
    if key in codes:
        code[key]['times'] += 1
