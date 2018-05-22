# coding: utf-8

from datetime import datetime
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from qingmi import db, cache


class Item(db.Document):
    """ 选项 """

    TYPE_INT = 'int'
    TYPE_STRING = 'string'
    TYPE_CHOICES = (
        (TYPE_INT, '整数'),
        (TYPE_STRING, '字符串'),
    )

    name = db.StringField(max_length=40, verbose_name='名称')
    key = db.StringField(max_length=40, verbose_name='键名')
    type = db.StringField(default=TYPE_INT, choices=TYPE_CHOICES, verbose_name='键名')