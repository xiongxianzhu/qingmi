# coding: utf-8

from datetime import datetime
from ..base import db, cache
from qingmi.utils import today


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
    value = db.DynamicField(verbose_name='值')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')

    meta = dict(
        indexes=[
            'key',
            '-created_at'
        ],
        ordering=['-created_at'],
    )

    @staticmethod
    # @cache.memoize(timeout=5)
    def get(key, default=0, name='None'):
        """ 获取整数类型的键值， 不存在则创建 """

        item = Item.objects(key=key).first()
        if item:
            return item.value

        Item(key=key, type=Item.TYPE_INT, value=default, name=name).save()
        return default

    @staticmethod
    def set(key, value, name=None):
        """ 设置整数类型的键值对， 不存在则创建 """

        item = Item.objects(key=key).first()
        if not item:
            item = Item(key=key)
        if name:
            item.name = name
        item.type = Item.TYPE_INT
        item.value = value
        item.updated_at = datetime.now()
        item.save()

    @staticmethod
    def inc(key, default=0, num=1, name=None):
        """ 整数类型的递增， 步长为num， 默认递增1； 不存在则创建 """

        params = dict(inc__value=num, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = Item.objects(key=key).modify(**params)
        if not item:
            params = dict(key=key, type=Item.TYPE_INT, value=default+num)
            if name:
                params['name'] = name
            Item(**params).save()
            return default + num
        else:
            return item.value + num

    @staticmethod
    # @cache.memoize(timeout=5)
    def text(key, default='', name=None):
        """ 获取字符串类型的键值， 不存在则创建 """

        item = Item.objects(key=key).first()
        if item:
            return item.value
        Item(key=key, type=Item.TYPE_STRING, value=default, name=name).save()
        return default

    @staticmethod
    def set_text(key, value, name=None):
        """ 设置字符串类型的键值， 不存在则创建 """

        item = Item.objects(key=key).first()
        if not item:
            item = Item(key=key)
        if name:
            item.name = name
        item.type = Item.TYPE_STRING
        item.value = value
        item.updated_at = datetime.now()
        item.save()

    @staticmethod
    def choice(key, value='', name=None, sep='|', coerce=str):
        return coerce(random.choice(Item.text(key, value, name).split(sep)))

    @staticmethod
    def list(key, value='', name=None, sep='|', coerce=int):
        return [coerce(x) for x in Item.text(key, value, name).split(sep)]

    @staticmethod
    def group(key, value='', name=None, sep='|', sub='-', coerce=int):
        texts = Item.text(key, value, name).split(sep)
        return [[coerce(y) for y in x.split(sub)] for x in texts]

    @staticmethod
    def hour(key, value='', name=None, sep='|', sub='-', default=None):
        h = datetime.now().hour
        for x in Item.group(key, value, name, sep, sub):
            if x[0] <= h <= x[1]:
                return x
        return default

    @staticmethod
    def bool(key, value=True, name=None):
        value = Item.text(key, 'true' if value else 'false', name)
        return True if value in ['true', 'True'] else False

    @staticmethod
    def time(key, value='', name=None):
        mat = "%Y-%m-%d %H:%M:%S"
        value = Item.text(key, datetime.now().strftime(mat), name)
        try:
            value = datetime.strptime(value, mat)
        except:
            pass
        return value


class StatsLog(db.Document):
    """ 统计日志 """
    
    key = db.StringField(verbose_name='键名')
    label = db.StringField(verbose_name='标签')
    day = db.StringField(verbose_name='日期')
    hour = db.IntField(default=0, verbose_name='小时')
    value = db.IntField(default=0, verbose_name='结果')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')

    meta = dict(
        indexes=[
            '-created_at',
            ('key', 'day', 'hour'),
            ('key', 'label', 'day', 'hour'),
        ]
    )

    @staticmethod
    def get(key, value=0, day=lambda: today(), hour=-1, save=True):
        """ 取值， 其中day是函数 """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = StatsLog.objects(key=key, day=day, hour=hour).first()
        if item:
            return item.value
        if save:
            StatsLog(key=key, day=day, hour=hour, value=value).save()
            return value
        return None

    @staticmethod
    def xget(key, value=0, day=None, hour=-1, save=True):
        """ 取值， 其中day为日期或时间的字符串或datetime.datetime实例 """
        day = str(day)[:10] if day else day
        item = StatsLog.objects(key=key, day=day, hour=hour).first()
        if item:
            return item.value
        if save:
            StatsLog(key=key, day=day, hour=hour, value=value).save()
            return value
        return None

    @staticmethod
    def get_bool(key, value=False, day=lambda: today(), hour=-1, save=True):
        value = StatsLog.get(key, 1 if value else 0, day, hour, save)
        if value is None:
            return None
        return True if value else False

    @staticmethod
    def xget_bool(key, value=False, day=None, hour=-1, save=True):
        value = StatsLog.xget(key, 1 if value else 0, day, hour, save)
        if value is None:
            return None
        return True if value else False

    @staticmethod
    def set_bool(key, value=False, day=lambda: today(), hour=-1, save=True):
        """ 设置value为bool型的值， 且日期为字符串为datetime.datetime类型， 默认当天 """
        if callable(day):
            day = day()
        day = str(day)[:10]
        value = 1 if value else 0
        item = StatsLog.objects(key=key, day=day, hour=hour).modify(
            set__value=value,
            set__day=day,
            set__hour=hour,
            set__updated_at=datetime.now(),
        )
        if item:
            return value
        if save:
            StatsLog(key=key, value=value, day=day, hour=hour).save()
            return value
        return None

    @staticmethod
    def xset_bool(key, value=False, day=None, hour=-1, save=True):
        """ 设置value为bool型的值， 且日期为字符串为datetime.datetime类型, 默认None """
        day = str(day)[:10] if day else day
        value = 1 if value else 0
        item = StatsLog.objects(key=key, day=day, hour=hour).modify(
            set__value=value,
            set__day=day,
            set__hour=hour,
            set__updated_at=datetime.now(),
        )
        if item:
            return value
        if save:
            StatsLog(key=key, value=value, day=day, hour=hour).save()
            return value
        return None

    @staticmethod
    def inc(key, day=lambda: today(), hour=-1, value=1):
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = StatsLog.objects(key=key, day=day, hour=hour).modify(
            inc__value=value,
            set__updated_at=datetime.now()
        )
        if not item:
            StatsLog(key=key, day=day, hour=hour, value=value).save()
            return value
        else:
            return item.value + value

    @staticmethod
    def date_inc(key, label='', value=1, day=None):
        day = datetime.now().strftime('%Y-%m-%d') if not day else day
        item = StatsLog.objects(key=key, label=label, day=day, hour=-1),modify(
            inc__value=value,
            set__updated_at=datetime.now()
        )
        if not item:
            StatsLog(key=key, label=label, day=day, hour=-1, value=value).save()
            return value
        else:
            return item.value + value

    @staticmethod
    def date_get(key, label='', day=None):
        day = datetime.strftime('%Y-%m-%d') if not day else day
        item = StatsLog.objects(key=key, label=label, day=day, hour=-1).first()
        return item.value if item else 0

    @staticmethod
    def date_set(key, label='', value=1, day=None):
        day = datetime.strftime('%Y-%m-%d') if not day else day
        item = StatsLog.objects(key=key, label=label, day=day, hour=-1).modify(
            value=value,
            set__updated_at=datetime.now()
        )
        if not item:
            StatsLog(key=key, label=label, day=day, hour=-1, value=value).save()
        return value
