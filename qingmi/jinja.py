# coding: utf-8

import re
from datetime import datetime
from flask import current_app, get_flashed_messages
from jinja2 import Environment, Markup
from xml.sax.saxutils import escape
from qingmi.utils import parse_datetime as _parse_datetime


__all__ = [
    'markup', 'markupper', 'first_error', 'JinjaManager', 'init_jinja',
]


def markup(html):
    return Markup(html) if current_app.jinja_env.autoescape else html


def markupper(func):
    def wrapper(*args, **kwargs):
        return markup(func(*args, **kwargs))
    return wrapper


def first_error(form):
    if form:
        for field in form:
            if field.errors:
                return field.errors[0]


class JinjaManager(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.jinja_env.filters.update(self.filters)

    @property
    def filters(self):
        """ 自定义jinja过滤器 """
        return dict(
            datetimeformat=self.datetimeformat,
            parse_datetime=self.parse_datetime,
            alert=self.alert_filter,
        )

    def datetimeformat(self, value, format='%Y-%m-%d %H:%M:%S'):
        if value:
            return value.strftime(format)
        return ''

    def parse_datetime(self, data):
        if data:
            return _parse_datetime(data)
        return ''

    @markupper
    def alert_msg(self, msg, style='danger'):
        style = 'info' if style == 'message' else style
        return '<div class="alert alert-%s"><button class="close" ' % (style) + \
            'type="button" data-dismiss="alert" aria-hidden="true">&times;' + \
            '</button><span>%s</span></div>' % (msg)
        # 下面代码与上等效
        # return markup('<div class="alert alert-%s"><button class="close" '
        #     'type="button" data-dismiss="alert" aria-hidden="true">&times;'
        #     '</button><span>%s</span></div>' % (style, msg))

    def alert_filter(self, form=None, style='danger'):
        error = first_error(form)
        if error:
            return self.alert_msg(error, style)

        messages = get_flashed_messages(with_categories=True)
        if messages and messages[-1][1] != 'Please log in to access this page.':
            return self.alert_msg(messages[-1][1], messages[-1][0] or 'danger')
        return ''


def init_jinja(app):
    jinja = JinjaManager()
    jinja.init_app(app)
