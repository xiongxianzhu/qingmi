# coding: utf-8

import random
from datetime import datetime
from qingmi.base import db, cache
from qingmi.utils import today


class Item(db.Document):
    """ 选项 """
    MENU_ICON = 'gear'
    
    TYPE = db.choices(INT='整数', FLOAT='浮点数', STRING='字符串', BOOLEAN='布尔值')

    name = db.StringField(max_length=40, verbose_name='名称')
    key = db.StringField(max_length=40, verbose_name='键名')
    data_type = db.StringField(default=TYPE.INT, choices=TYPE.CHOICES, verbose_name='类型')
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
        """ 取值(整型/浮点型) """
        item = Item.objects(key=key).first()
        if item:
            try:
                if item.data_type == Item.TYPE.INT:
                    return int(item.value)
                if item.data_type == Item.TYPE.FLOAT:
                    return float(item.value)
            except ValueError as e:
                return 0
        data_type = Item.TYPE.FLOAT if type(value) is float else Item.TYPE.INT
        Item(key=key, data_type=data_type, value=value, name=name).save()
        return value

    @staticmethod
    def set(key, value=0, name=None):
        """ 设置值(整型/浮点型) """
        item = Item.objects(key=key).first()
        if not item:
            item = Item(key=key)
        if name:
            item.name = name
        item.data_type = Item.TYPE.FLOAT if type(value) is float else Item.TYPE.INT
        item.value = value
        item.updated_at = datetime.now()
        item.save()

    @staticmethod
    def inc(key, start=0, value=1, name=None):
        """ 递增，步长为num， 默认递增1； 不存在则创建 """
        params = dict(inc__value=value, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = Item.objects(key=key).modify(**params)
        if not item:
            params = dict(key=key, data_type=Item.TYPE.INT, value=start+value)
            if name:
                params['name'] = name
            Item(**params).save()
            return start + value
        else:
            return item.value + value

    @staticmethod
    # @cache.memoize(timeout=5)
    def text(key, value='', name=None):
        """ 取值(字符串) """
        item = Item.objects(key=key).first()
        if item:
            return str(item.value)
        Item(key=key, data_type=Item.TYPE.STRING, value=value, name=name).save()
        return value

    @staticmethod
    def set_text(key, value='', name=None):
        """ 设置值(字符串) """
        item = Item.objects(key=key).first()
        if not item:
            item = Item(key=key)
        if name:
            item.name = name
        item.data_type = Item.TYPE.STRING
        item.value = value
        item.updated_at = datetime.now()
        item.save()

    @staticmethod
    # @cache.memoize(timeout=5)
    def bool(key, value=False, name=None):
        """ 取值(布尔类型) """
        item = Item.objects(key=key).first()
        if item:
            return True if item.value in ['true', 'True'] else False
        Item(key=key, data_type=Item.TYPE.BOOLEAN, value=value, name=name).save()
        return value

    @staticmethod
    def set_bool(key, value=False, name=None):
        """ 设置值(布尔类型) """
        item = Item.objects(key=key).first()
        if not item:
            item = Item(key=key)
        if name:
            item.name = name
        item.data_type = Item.TYPE.BOOLEAN
        item.value = value
        item.updated_at = datetime.now()
        item.save()
        return True if value in ['true', 'True'] else False

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
    def time(key, value='', name=None):
        mat = "%Y-%m-%d %H:%M:%S"
        value = Item.text(key, datetime.now().strftime(mat), name)
        try:
            value = datetime.strptime(value, mat)
        except:
            pass
        return value


# class StatsLog(db.Document):
#     """ 统计日志 """
#     MENU_ICON = 'bar-chart'
    
#     key = db.StringField(verbose_name='键名')
#     uid = db.StringField(verbose_name='用户ID')
#     xid = db.StringField(verbose_name='其他ID')
#     label = db.StringField(verbose_name='标签')
#     day = db.StringField(verbose_name='日期')
#     hour = db.IntField(default=0, verbose_name='小时')
#     value = db.IntField(default=0, verbose_name='结果')
#     created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')
#     updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')

#     meta = dict(
#         indexes=[
#             '-created_at',
#             ('key', 'day', 'hour'),
#             ('key', 'uid', 'xid', 'label', 'day', 'hour'),
#         ],
#         ordering=['-created_at'],
#     )

#     @staticmethod
#     def get(key, uid='', xid='', label='', day=lambda: today(), hour=-1, value=0, save=True):
#         """ 取值 """
#         if callable(day):
#             day = day()
#         day = str(day)[:10]
#         item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label, day=day, hour=hour).first()
#         if item:
#             return item.value
#         if save:
#             StatsLog(key=key, uid=uid, xid=xid, label=label, day=day, hour=hour, value=value).save()
#             return value
#         return None

#     @staticmethod
#     def set(key, uid='', xid='', label='', day=lambda: today(), hour=-1, value=0, save=True):
#         """ 设置值 """
#         if callable(day):
#             day = day()
#         day = str(day)[:10]
#         item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label, day=day, hour=hour).modify(
#             set__value=value,
#             set__updated_at=datetime.now(),
#         )
#         if item:
#             return value
#         if save:
#             StatsLog(key=key, uid=uid, xid=xid, label=label, day=day, hour=hour, value=value).save()
#             return value
#         return None

#     @staticmethod
#     def inc(key, uid='', xid='', label='', day=lambda: today(), hour=-1, start=0, value=1, save=True):
#         """ 递增 """
#         if callable(day):
#             day = day()
#         day = str(day)[:10]
#         item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label, day=day, hour=hour).modify(
#             inc__value=value,
#             set__updated_at=datetime.now()
#         )
#         if item:
#             return item.value + value
#         if save:
#             StatsLog(key=key, uid=uid, xid=xid, label=label, day=day, hour=hour, value=start+value).save()
#             return start+value
#         return None

#     @staticmethod
#     def xget(key, uid='', xid='', label='', day='', hour=-1, value=0, save=True):
#         """ 取值 """
#         return StatsLog.get(key, uid, xid, label, day, hour, value, save)

#     @staticmethod
#     def xset(key, uid='', xid='', label='', day='', hour=-1, value=0, save=True):
#         """ 设置值 """
#         return StatsLog.set(key, uid, xid, label, day, hour, value, save)

#     @staticmethod
#     def xinc(key, uid='', xid='', label='', day='', hour=-1, start=0, value=1, save=True):
#         """ 递增 """
#         return StatsLog.inc(key, uid, xid, label, day, hour, start, value, save)

#     @staticmethod
#     def get_bool(key, uid='', xid='', label='', day=lambda: today(), hour=-1, value=False, save=True):
#         """ 取布尔值 """
#         value = StatsLog.get(key, uid, xid, label, day, hour, 1 if value else 0, save)
#         if value is None:
#             return None
#         if value is 1:
#             return True
#         return False

#     @staticmethod
#     def set_bool(key, uid='', xid='', label='', day=lambda: today(), hour=-1, value=False, save=True):
#         """ 设置布尔值 """
#         value = StatsLog.set(key, uid, xid, label, day, hour, 1 if value else 0, save)
#         if value is None:
#             return None
#         if value is 1:
#             return True
#         return False

#     @staticmethod
#     def xget_bool(key, uid='', xid='', label='', day='', hour=-1, value=False, save=True):
#         """ 取布尔值 """
#         return StatsLog.get_bool(key, uid, xid, label, day, hour, value, save)
        
#     @staticmethod
#     def xset_bool(key, uid='', xid='', label='', day='', hour=-1, value=False, save=True):
#         """ 设置布尔值 """
#         return StatsLog.set_bool(key, uid, xid, label, day, hour, value, save)


class StatsLog(db.Document):
    """ 统计日志 """
    MENU_ICON = 'bar-chart'

    TYPE = db.choices(INT='整数', FLOAT='浮点数', STRING='字符串', BOOLEAN='布尔值')

    name = db.StringField(max_length=40, verbose_name='名称')
    key = db.StringField(max_length=128, verbose_name='键名')
    uid = db.StringField(max_length=128, verbose_name='用户ID')
    xid = db.StringField(max_length=128, verbose_name='其他ID')
    data_type = db.StringField(default=TYPE.INT, choices=TYPE.CHOICES, verbose_name='类型')
    label = db.StringField(max_length=128, verbose_name='标签')
    day = db.StringField(max_length=20, verbose_name='日期')
    hour = db.IntField(default=0, verbose_name='小时')
    value = db.DynamicField(verbose_name='值')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')

    meta = dict(
        indexes=[
            'key',
            '-created_at',
            '-updated_at',
            ('key', 'uid'),
            ('key', 'day', 'hour'),
            ('key', 'uid', 'xid', 'label', 'day', 'hour'),
        ],
        ordering=['-created_at'],
    )

    @staticmethod
    def get(key, uid='', xid='', label='', day=lambda: today(),
            hour=-1, value=0, name=None, save=True):
        """ 取值(整型/浮点型) """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label, day=day, hour=hour).first()
        if item:
            if name:
                item.name = name
                item.save()
            try:
                if item.data_type == Item.TYPE.INT:
                    return int(item.value)
                if item.data_type == Item.TYPE.FLOAT:
                    return float(item.value)
            except ValueError as e:
                return 0
        if save:
            data_type = StatsLog.TYPE.FLOAT if type(value) is float else StatsLog.TYPE.INT
            StatsLog(key=key, data_type=data_type, uid=uid, xid=xid, label=label, day=day,
                    hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def set(key, uid='', xid='', label='', day=lambda: today(),
            hour=-1, value=0, name=None, save=True):
        """ 设置值(整型/浮点型) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        data_type = StatsLog.TYPE.FLOAT if type(value) is float else StatsLog.TYPE.INT
        params = dict(set__value=value, set__data_type=data_type, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label,
                    day=day, hour=hour).modify(**params)
        if item:
            return value
        if save:
            StatsLog(key=key, data_type=data_type, uid=uid, xid=xid, label=label,
                day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def inc(key, uid='', xid='', label='', day=lambda: today(),
            hour=-1, start=0, value=1, name=None, save=True):
        """ 递增(整型/浮点型) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        data_type = StatsLog.TYPE.FLOAT if type(value) is float else StatsLog.TYPE.INT
        params = dict(inc__value=value, set__data_type=data_type, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label,
                            day=day, hour=hour).modify(**params)
        if item:
            return item.value + value
        if save:
            StatsLog(key=key, data_type=data_type, uid=uid, xid=xid, label=label,
                day=day, hour=hour, value=start+value, name=name).save()
            return start+value
        return None

    @staticmethod
    def text(key, uid='', xid='', label='', day=lambda: today(),
            hour=-1, value='', name=None, save=True):
        """ 取值(字符串) """
        if callable(day):
            day = day()
        day = str(day)[:10]
        item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label,
                            day=day, hour=hour).first()
        if item:
            if name:
                item.name = name
                item.save()
            return item.value
        if save:
            StatsLog(key=key, data_type=StatsLog.TYPE.STRING, uid=uid, xid=xid, label=label,
                day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def set_text(key, uid='', xid='', label='', day=lambda: today(),
                hour=-1, value='', name=None, save=True):
        """ 设置值(字符串) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        params = dict(set__value=value, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label,
                    day=day, hour=hour).modify(**params)
        if item:
            return value
        if save:
            StatsLog(key=key, data_type=StatsLog.TYPE.STRING, uid=uid, xid=xid, label=label,
                day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def bool(key, uid='', xid='', label='', day=lambda: today(), hour=-1,
                value=False, name=None, save=True):
        """ 取值(布尔值) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        if type(value) is not bool:
            raise ValueError('Invalid value: %s, %s is not a boolean type value.' % (value, value))

        item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label,
                            day=day, hour=hour).first()
        if item:
            if name:
                item.name = name
                item.save()
            return item.value
        if save:
            StatsLog(key=key, data_type=StatsLog.TYPE.BOOLEAN, uid=uid, xid=xid, label=label,
                day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def set_bool(key, uid='', xid='', label='', day=lambda: today(), hour=-1,
                    value=False, name=None, save=True):
        """ 设置值(布尔值) """
        if callable(day):
            day = day()
        day = str(day)[:10]

        if type(value) is not bool:
            raise ValueError('Invalid value: %s, %s is not a boolean type value.' % (value, value))

        params = dict(set__value=value, set__updated_at=datetime.now())
        if name:
            params['set__name'] = name
        item = StatsLog.objects(key=key, uid=uid, xid=xid, label=label, day=day,
                            hour=hour).modify(**params)
        if item:
            return value
        if save:
            StatsLog(key=key, data_type=StatsLog.TYPE.BOOLEAN, uid=uid, xid=xid, label=label,
                day=day, hour=hour, value=value, name=name).save()
            return value
        return None

    @staticmethod
    def xget(key, uid='', xid='', label='', day='', hour=-1,
                value=0, name=None, save=True):
        """ 取值 """
        return StatsLog.get(key, uid, xid, label, day, hour, value, name, save)

    @staticmethod
    def xset(key, uid='', xid='', label='', day='', hour=-1,
                value=0, name=name, save=True):
        """ 设置值 """
        return StatsLog.set(key, uid, xid, label, day, hour, value, name, save)

    @staticmethod
    def xinc(key, uid='', xid='', label='', day='', hour=-1,
                start=0, value=1, name=None, save=True):
        """ 递增 """
        return StatsLog.inc(key, uid, xid, label, day, hour, start, value, name, save)

    @staticmethod
    def xtext(key, uid='', xid='', label='', day='', hour=-1,
                value='', name=None, save=True):
        """ 取值(字符串) """
        return StatsLog.text(key, uid, xid, label, day, hour, value, name, save)

    @staticmethod
    def xset_text(key, uid='', xid='', label='', day='',
                hour=-1, value='', name=None, save=True):
        """ 设置值(字符串) """
        return StatsLog.set_text(key, uid, xid, label, day, hour, value, name, save)

    @staticmethod
    def xbool(key, uid='', xid='', label='', day='', hour=-1,
                value=False, name=None, save=True):
        """ 取值(布尔值) """
        return StatsLog.bool(key, uid, xid, label, day, hour, value, name, save)

    @staticmethod
    def xset_bool(key, uid='', xid='', label='', day='', hour=-1,
                    value=False, name=None, save=True):
        """ 设置值(布尔值) """
        return StatsLog.set_bool(key, uid, xid, label, day, hour, value, name, save)

    @staticmethod
    def choice(key, uid='', xid='', label='', day=lambda: today(),
                hour=-1, value='', name=None, save=True, sep='|', coerce=str):
        return coerce(random.choice(StatsLog.text(key, uid=uid, xid=xid,
                        label=label, day=day, hour=hour,
                        value=value, name=name, save=save).split(sep)))

    @staticmethod
    def xchoice(key, uid='', xid='', label='', day='', hour=-1,
                value='', name=None, save=True, sep='|', coerce=str):
        return coerce(random.choice(StatsLog.xtext(key, uid=uid, xid=xid,
                        label=label, day=day, hour=hour,
                        value=value, name=name, save=save).split(sep)))

    @staticmethod
    def list(key, uid='', xid='', label='', day=lambda: today(),
                hour=-1, value='', name=None, save=True,
                sep='|', coerce=int):
        """ 将特定格式的字符串转为一维数组 """
        """ 例如， 字符串格式为'1|2|3|4'， 返回的是[1, 2, 3, 4] """
        text = StatsLog.text(key, uid=uid, xid=xid,
                        label=label, day=day, hour=hour,
                        value=value, name=name, save=save)
        if not text:
            return None
        texts = text.split(sep)
        return [coerce(x) for x in texts]

    @staticmethod
    def xlist(key, uid='', xid='', label='', day='', hour=-1,
                value='', name=None, save=True, sep='|', coerce=int):
        """ 将特定格式的字符串转为一维数组 """
        """ 例如， 字符串格式为'1|2|3|4'， 返回的是[1, 2, 3, 4] """
        text = StatsLog.xtext(key, uid=uid, xid=xid,
                        label=label, day=day, hour=hour,
                        value=value, name=name, save=save)
        if not text:
            return None
        texts = text.split(sep)
        return [coerce(x) for x in texts]

    @staticmethod
    def group(key, uid='', xid='', label='', day=lambda: today(),
                hour=-1, value='', name=None, save=True,
                sep='|', sub='-', coerce=int):
        """ 将特定格式的字符串转为二维数组 """
        """ 例如， 字符串格式为'1-3|4-9|10-32|64-128'， 
            返回的是[[1, 3], [4, 9], [10, 32], [64, 128]]
        """
        text = StatsLog.text(key, uid=uid, xid=xid,
                        label=label, day=day, hour=hour,
                        value=value, name=name, save=save)
        if not text:
            return None
        texts = text.split(sep)
        return [[coerce(y) for y in x.split(sub)] for x in texts]

    @staticmethod
    def xgroup(key, uid='', xid='', label='', day='', hour=-1,
                value='', name=None, save=True,
                sep='|', sub='-', coerce=int):
        """ 将特定格式的字符串转为二维数组 """
        """ 例如， 字符串格式为'1-3|4-9|10-32|64-128'， 
            返回的是[[1, 3], [4, 9], [10, 32], [64, 128]]
        """
        text = StatsLog.xtext(key, uid=uid, xid=xid,
                        label=label, day=day, hour=hour,
                        value=value, name=name, save=save)
        texts = text.split(sep)
        return [[coerce(y) for y in x.split(sub)] for x in texts]

    @staticmethod
    def hour_range(key, uid='', xid='', label='', day=lambda: today(),
                hour=-1, value='', name=None, save=True,
                sep='|', sub='-', default=None):
        """ 获取当前时间整点所在的整点区间 """
        """ 例如， 当前时间的整点是10点， value为'3-8|9-14|15-23', 则10在区间[9, 14]之间，
                返回的值是[9, 14]
        """
        groups = StatsLog.group(key, uid=uid, xid=xid,
                        label=label, day=day, hour=hour,
                        value=value, name=name, save=save,
                        sep=sep, sub=sub)
        if not groups:
            return None
        h = datetime.now().hour
        for x in groups:
            if x[0] <= h <= x[1]:
                return x
        return default

    @staticmethod
    def xhour_range(key, uid='', xid='', label='', day='', hour=-1,
                value='', name=None, save=True,
                sep='|', sub='-', default=None):
        """ 获取当前时间整点所在的整点区间 """
        """ 例如， 当前时间的整点是10点， value为'3-8|9-14|15-23', 则10在区间[9, 14]之间，
                返回的值是[9, 14]
        """
        groups = StatsLog.xgroup(key, uid=uid, xid=xid,
                        label=label, day=day, hour=hour,
                        value=value, name=name, save=save,
                        sep=sep, sub=sub)
        if not groups:
            return None
        h = datetime.now().hour
        for x in groups:
            if x[0] <= h <= x[1]:
                return x
        return default


class Image(db.Document):
    """ 图片 """
    key = db.StringField(max_length=128, verbose_name='KEY')
    name = db.StringField(max_length=128, verbose_name='图片名称')
    image = db.XImageField(verbose_name='图片')
    # image = db.StringField(verbose_name='图片名称')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')

    def __unicode__(self):
        return '%s-%s' % (self.key, self.name)
