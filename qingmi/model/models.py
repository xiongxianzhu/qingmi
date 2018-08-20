# coding: utf-8

import random
from datetime import datetime
from qingmi.base import db, cache
from qingmi.utils import today


class Item(db.Document):
    """ 选项 """
    MENU_ICON = 'gear'

    # TYPE.INT = 'INT'
    # TYPE.STRING = 'STRING'
    # TYPE_CHOICES = (
    #     (TYPE.INT, '整数'),
    #     (TYPE.STRING, '字符串'),
    # )
    # 
    
    TYPE = db.choices(INT='整数', FLOAT='浮点数', STRING='字符串', BOOLEAN='布尔值')

    name = db.StringField(max_length=40, verbose_name='名称')
    key = db.StringField(max_length=40, verbose_name='键名')
    type = db.StringField(default=TYPE.INT, choices=TYPE.CHOICES, verbose_name='类型')
    # type = db.StringField(default=TYPE.INT, choices=TYPE_CHOICES, verbose_name='类型')
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
    def get(key, value=0, name=None):
        """ 获取整数类型的键值， 不存在则创建 """
        item = Item.objects(key=key).first()
        if item:
            return item.value

        Item(key=key, type=Item.TYPE.INT, value=value, name=name).save()
        return value

    @staticmethod
    def set(key, value=0, name=None):
        """ 设置整数类型的键值对， 不存在则创建 """
        item = Item.objects(key=key).first()
        if not item:
            item = Item(key=key)
        if name:
            item.name = name
        item.type = Item.TYPE.INT
        item.value = value
        item.updated_at = datetime.now()
        item.save()

    @staticmethod
    def inc(key, start=0, value=1, name=None):
        """ 整数类型的递增，步长为num， 默认递增1； 不存在则创建 """
        params = dict(inc__value=value, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = Item.objects(key=key).modify(**params)
        if not item:
            params = dict(key=key, type=Item.TYPE.INT, value=start+value)
            if name:
                params['name'] = name
            Item(**params).save()
            return start + value
        else:
            return item.value + value

    @staticmethod
    # @cache.memoize(timeout=5)
    def text(key, value='', name=None):
        """ 获取字符串类型的键值 """
        item = Item.objects(key=key).first()
        if item:
            return item.value
        Item(key=key, type=Item.TYPE.STRING, value=value, name=name).save()
        return value

    @staticmethod
    def set_text(key, value='', name=None):
        """ 设置字符串类型的键值 """
        item = Item.objects(key=key).first()
        if not item:
            item = Item(key=key)
        if name:
            item.name = name
        item.type = Item.TYPE.STRING
        item.value = value
        item.updated_at = datetime.now()
        item.save()

    @staticmethod
    # @cache.memoize(timeout=5)
    def bool(key, value=False, name=None):
        """ 获取布尔类型的键值 """
        item = Item.objects(key=key).first()
        if item:
            return item.value
        Item(key=key, type=Item.TYPE.BOOLEAN, value=value, name=name).save()
        return value

    @staticmethod
    def set_bool(key, value=False, name=None):
        """ 设置布尔类型的键值 """
        item = Item.objects(key=key).first()
        if not item:
            item = Item(key=key)
        if name:
            item.name = name
        item.type = Item.TYPE.BOOLEAN
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

    # @staticmethod
    # def bool(key, value=True, name=None):
    #     value = Item.text(key, 'true' if value else 'false', name)
    #     return True if value in ['true', 'True'] else False

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
    MENU_ICON = 'bar-chart'
    
    key = db.StringField(verbose_name='键名')
    uid = db.StringField(verbose_name='用户ID')
    oid = db.StringField(verbose_name='其他ID')
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
            ('key', 'uid', 'oid', 'label', 'day', 'hour'),
        ]
    )

    @staticmethod
    def get(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value=0, save=True):
        """ 取值 """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = StatsLog.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).first()
        if item:
            return item.value
        if save:
            StatsLog(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour, value=value).save()
            return value
        return None

    @staticmethod
    def set(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value=0, save=True):
        """ 设置值 """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = StatsLog.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).modify(
            set__value=value,
            set__updated_at=datetime.now(),
        )
        if item:
            return value
        if save:
            StatsLog(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour, value=value).save()
            return value
        return None

    @staticmethod
    def inc(key, uid='', oid='', label='', day=lambda: today(), hour=-1, start=0, value=1, save=True):
        """ 递增 """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = StatsLog.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).modify(
            inc__value=value,
            set__updated_at=datetime.now()
        )
        if item:
            return item.value + value
        if save:
            StatsLog(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour, value=start+value).save()
            return start+value
        return None

    @staticmethod
    def xget(key, uid='', oid='', label='', day='', hour=-1, value=0, save=True):
        """ 取值 """
        return StatsLog.get(key, uid, oid, label, day, hour, value, save)

    @staticmethod
    def xset(key, uid='', oid='', label='', day='', hour=-1, value=0, save=True):
        """ 设置值 """
        return StatsLog.set(key, uid, oid, label, day, hour, value, save)

    @staticmethod
    def xinc(key, uid='', oid='', label='', day='', hour=-1, start=0, value=1, save=True):
        """ 递增 """
        return StatsLog.inc(key, uid, oid, label, day, hour, start, value, save)

    @staticmethod
    def get_bool(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value=False, save=True):
        """ 取布尔值 """
        value = StatsLog.get(key, uid, oid, label, day, hour, 1 if value else 0, save)
        if value is None:
            return None
        if value is 1:
            return True
        return False

    @staticmethod
    def set_bool(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value=False, save=True):
        """ 设置布尔值 """
        value = StatsLog.set(key, uid, oid, label, day, hour, 1 if value else 0, save)
        if value is None:
            return None
        if value is 1:
            return True
        return False

    @staticmethod
    def xget_bool(key, uid='', oid='', label='', day='', hour=-1, value=False, save=True):
        """ 取布尔值 """
        return StatsLog.get_bool(key, uid, oid, label, day, hour, value, save)
        
    @staticmethod
    def xset_bool(key, uid='', oid='', label='', day='', hour=-1, value=False, save=True):
        """ 设置布尔值 """
        return StatsLog.set_bool(key, uid, oid, label, day, hour, value, save)


class Log(db.Document):
    """ 日志 """
    MENU_ICON = 'gears'

    TYPE = db.choices(INT='整数', FLOAT='浮点数', STRING='字符串', BOOLEAN='布尔值')

    name = db.StringField(max_length=40, verbose_name='名称')
    key = db.StringField(verbose_name='键名')
    uid = db.StringField(verbose_name='用户ID')
    oid = db.StringField(verbose_name='其他ID')
    type = db.StringField(default=TYPE.INT, choices=TYPE.CHOICES, verbose_name='类型')
    label = db.StringField(verbose_name='标签')
    day = db.StringField(verbose_name='日期')
    hour = db.IntField(default=0, verbose_name='小时')
    value = db.DynamicField(verbose_name='值')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')

    meta = dict(
        indexes=[
            'key',
            '-created_at',
            ('key', 'uid', 'oid', 'label', 'day', 'hour'),
        ],
        ordering=['-created_at'],
    )

    @staticmethod
    def get(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value=0, name=None, save=True):
        """ 取值(整型) """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = Log.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).first()
        if item:
            return item.value
        if save:
            Log(key=key, type=Log.TYPE.INT, uid=uid, oid=oid, label=label, day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def set(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value=0, name=None, save=True):
        """ 设置值(整型) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        params = dict(set__value=value, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = Log.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).modify(**params)
        if item:
            return value
        if save:
            Log(key=key, type=Log.TYPE.INT, uid=uid, oid=oid, label=label, day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def inc(key, uid='', oid='', label='', day=lambda: today(), hour=-1, start=0, value=1, name=None, save=True):
        """ 递增(整型) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        params = dict(inc__value=value, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = Log.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).modify(**params)
        if item:
            return item.value + value
        if save:
            Log(key=key, type=Log.TYPE.INT, uid=uid, oid=oid, label=label, day=day, hour=hour, value=start+value, name=name).save()
            return start+value
        return None

    @staticmethod
    def text(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value='', name=None, save=True):
        """ 取值(字符串) """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = Log.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).first()
        if item:
            return item.value
        if save:
            Log(key=key, type=Log.TYPE.STRING, uid=uid, oid=oid, label=label, day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def set_text(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value='', name=None, save=True):
        """ 设置值(字符串) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        params = dict(set__value=value, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = Log.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).modify(**params)
        if item:
            return value
        if save:
            Log(key=key, type=Log.TYPE.STRING, uid=uid, oid=oid, label=label, day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def bool(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value=False, name=None, save=True):
        """ 取值(布尔值) """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = Log.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).first()
        if item:
            return item.value
        if save:
            Log(key=key, type=Log.TYPE.BOOLEAN, uid=uid, oid=oid, label=label, day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def set_bool(key, uid='', oid='', label='', day=lambda: today(), hour=-1, value=False, name=None, save=True):
        """ 设置值(布尔值) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        params = dict(set__value=value, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = Log.objects(key=key, uid=uid, oid=oid, label=label, day=day, hour=hour).modify(**params)
        if item:
            return value
        if save:
            Log(key=key, type=Log.TYPE.BOOLEAN, uid=uid, oid=oid, label=label, day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def xget(key, uid='', oid='', label='', day='', hour=-1, value=0, name=None, save=True):
        """ 取值 """
        return Log.get(key, uid, oid, label, day, hour, value, name, save)

    @staticmethod
    def xset(key, uid='', oid='', label='', day='', hour=-1, value=0, name=name, save=True):
        """ 设置值 """
        return Log.set(key, uid, oid, label, day, hour, value, name, save)

    @staticmethod
    def xinc(key, uid='', oid='', label='', day='', hour=-1, start=0, value=1, name=None, save=True):
        """ 递增 """
        return Log.inc(key, uid, oid, label, day, hour, start, value, name, save)

    @staticmethod
    def xtext(key, uid='', oid='', label='', day='', hour=-1, start=0, value=1, name=None, save=True):
        """ 取值(字符串) """
        return Log.text(key, uid, oid, label, day, hour, start, value, name, save)

    @staticmethod
    def set_xtext(key, uid='', oid='', label='', day='', hour=-1, start=0, value=1, name=None, save=True):
        """ 设置值(字符串) """
        return Log.set_text(key, uid, oid, label, day, hour, start, value, name, save)

    @staticmethod
    def xbool(key, uid='', oid='', label='', day='', hour=-1, start=0, value=1, name=None, save=True):
        """ 取值(布尔值) """
        return Log.bool(key, uid, oid, label, day, hour, start, value, name, save)

    @staticmethod
    def set_xbool(key, uid='', oid='', label='', day='', hour=-1, start=0, value=1, name=None, save=True):
        """ 设置值(布尔值) """
        return Log.set_bool(key, uid, oid, label, day, hour, start, value, name, save)
    
    @staticmethod
    def choice(key, value='', name=None, sep='|', coerce=str):
        return coerce(random.choice(Log.xtext(key, value=value, name=name).split(sep)))

    @staticmethod
    def xlist(key, value='', name=None, sep='|', coerce=int):
        return [coerce(x) for x in Log.xtext(key, value=value, name=name).split(sep)]

    @staticmethod
    def list(key, day=lambda: today(), value='', name=None, sep='|', coerce=int):
        return [coerce(x) for x in Log.text(key, day=day, value=value, name=name).split(sep)]

    @staticmethod
    def group(key, value='', name=None, sep='|', sub='-', coerce=int):
        texts = Log.xtext(key, value=value, name=name).split(sep)
        return [[coerce(y) for y in x.split(sub)] for x in texts]

    @staticmethod
    def _hour(key, value='', name=None, sep='|', sub='-', default=None):
        h = datetime.now().hour
        for x in Log.group(key, value=value, name=name, sep=sep, sub=sub):
            if x[0] <= h <= x[1]:
                return x
        return default
