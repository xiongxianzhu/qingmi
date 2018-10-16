# coding: utf-8
"""
统计助手(statistics helper)
使用了开源项目: https://github.com/highcharts/highcharts， 作为统计图表
"""

import time
import functools
from datetime import datetime, timedelta
from flask import request
from qingmi.model import StatsLog


def get_date_ranger(date_start, date_end):
    """获取日期区间
    :param date_start
    :param date_end
    """
    dates = []
    start = datetime.strptime(date_start, '%Y-%m-%d')
    end = datetime.strptime(date_end, '%Y-%m-%d')
    size = (end - start).days

    if size > 0:
        for i in range(size+1):
            dates.append((start + timedelta(days=i)).strftime('%Y-%m-%d'))
    return dates


def get_date(key='day'):
    """获取日期
    :param key
    """
    day = request.args.get(key, '')
    try:
        datetime.strptime(day, '%Y-%m-%d')
    except ValueError:
        day = time.strftime('%Y-%m-%d')
    return day


def get_dates(stats=True, start_key='start', end_key='end', start='', end=''):
    """获取日期区间两端的日期
    """
    if callable(start):
        start = start()
    if callable(end):
        end = end()

    start = request.args.get(start_key, start)
    end = request.args.get(end_key, end)

    try:
        datetime.strptime(start, '%Y-%m-%d')
        datetime.strptime(end, '%Y-%m-%d')
    except (ValueError, TypeError):
        start = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        end = datetime.now().strftime('%Y-%m-%d')

    if stats is True:
        days = get_date_ranger(start, end)
        if len(days) == 0:
            start = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
            end = datetime.now().strftime('%Y-%m-%d')

    return start, end


def get_value_list(key, days, uid=None):
    query = dict(key=key, day__in=days)
    if uid:
        query['uid'] = uid

    length = len(days)
    value_list = [0] * length
    # 上面方式优雅， 但如果列表包含了列表， 上样这样做会产生浅拷贝， 则采用以下方式
    # value_list = [0 for i in range(length)]
    items = StatsLog.objects(**query)
    for item in items:
        value_list[days.index(item.day)] = item.value
    return value_list


def get_hour_list(key, day, uid=None, hour=23):

    query = dict(key=key, day=day)
    if uid:
        query['uid'] = uid

    items = StatsLog.objects(**query)
    values = [0 for i in range(hour + 1)]
    for item in items:
        if item.hour <= hour:
            values[item.hour] = item.value
    return values


def hour_value_list(day, key, *args, **kwargs):
    return get_hour_list(key, day, **kwargs)


def get_value(value, value2, default=True):
    """ 获得比值 """
    if value == 0:
        return 0
    if value2 == 0 or not value2:
        result = value * 100.0 / abs(value)
    else:
        result = value * 100.0 / value2

    if result < -20 and default:
        return -20
    elif result > 120 and default:
        return 120
    return result


def get_sum_value(data):
    """ 多个值打包成一个 """
    values = zip
    for v in data:
        values = functools.partial(values, v)
    return list(map(lambda x: sum(x), values()))


def date_value(key, days):
    """ 获取一个key的值或多个key的和 """
    if isinstance(key, list):
        value_list = [get_value_list('date_%s' % x, days) for x in key]
        return get_sum_value(value_list)
    return get_value_list('date_%s' % key, days)


def hour_value(key, day):
    """ 获取一个key的值或多个key的和 """
    if isinstance(key, list):
        value_list = [get_hour_list('hour_%s' % x, day) for x in key]
        return get_sum_value(value_list)
    return get_hour_list('hour_%s' % key, day)


def change_value_list(data, key, days):
    style = data.get('style', '/')
    key_data = date_value(data.get('key'), days)
    key2_data = date_value(data.get('key2'), days)
    if style == '+':
        return list(map(lambda x: x[0] + x[1], zip(key_data, key2_data)))
    if style == '-':
        return list(map(lambda x: x[0] - x[1], zip(key_data, key2_data)))
    return list(map(lambda x: get_value(x[0], x[1], data.get('default', True)), zip(key_data, key2_data)))


def hour_change_value_list(data, day, key, *args, **kwargs):
    style = data.get('style', '/')
    key_data = hour_value(data.get('key'), day)
    key2_data = hour_value(data.get('key2'), day)
    if style == '+':
        return list(map(lambda x: x[0] + x[1], zip(key_data, key2_data)))
    if style == '-':
        return list(map(lambda x: x[0] - x[1], zip(key_data, key2_data)))
    return list(map(lambda x: get_value(x[0], x[1], data.get('default', True)), zip(key_data, key2_data)))


class StatsHelper(object):
    """ 统计助手 """

    def __init__(self):
        self.items = []
        self.funcs = []
        self.start = datetime(2018, 1, 1)
        self.minutes = 1

    def _save(self, key, value, day, hour, **kwargs):
        if callable(value):
            value = value(**kwargs)

        if type(value) is list:
            for item in value:
                if type(item['value']) == dict:
                    for k, v in item['value'].items():
                        query = dict(key=key.format(id=item['_id'], key=k),
                                    day=day, hour=hour)
                        StatsLog.objects(**query).update(
                            set__value=v,
                            set__updated_at=datetime.now(),
                            set_on_insert__created_at=datetime.now(),
                            upsert=True,
                        )
                else:
                    StatsLog.objects(key=key.format(**item), day=day,
                        hour=hour).update(
                        set__value=item['value'],
                        set__updated_at=datetime.now(),
                        set_on_insert__created_at=datetime.now(),
                        upsert=True,
                    )
        else:
            StatsLog.objects(key=key, day=day, hour=hour).update(
                set__value=value,
                set__updated_at=datetime.now(),
                set_on_insert__created_at=datetime.now(),
                upsert=True,
            )

    def save(self, key, value, day, start, end, hour=0, field='created_at', **kwargs):
        if field is not None:
            kwargs.setdefault('%s__gte' % field, start)
            kwargs.setdefault('%s__lt' % field, end)
        self._save(key, value, day, hour, **kwargs)

    def stats(self, key, model, query=lambda x: x.count(), handle=lambda x: x, **kwargs):
        self.items.append(dict(
            key=key,
            model=model,
            query=query,
            handle=handle,
            kwargs=kwargs,
        ))

    def count(self, key, model, **kwargs):
        """ 计数 """
        self.stats(key, model, **kwargs)

    def sum(self, key, model, sub, **kwargs):
        """ 求和 """
        # lambda x中的x为queryset
        self.stats(key, model, query=lambda x: x.aggregate_sum(sub), **kwargs)

    def distinct(self, key, model, sub, **kwargs):
        self.stats(key, model, query=lambda x: x.distinct(sub), handle=len, **kwargs)

    def aggregate(self, key, model, *pipline, **kwargs):
        self.stat(key, model, query=lambda x: list(x.aggregate(*pipline)), **kwargs)

    def aggregate2(self, key, model, model2, sub, *pipline, **kwargs):
        handle = lambda x: list(model.objects(id__in=x).aggregate(*pipline))
        query = lambda x: x.distinct(sub)
        self.stats(key, model2, query=query, handle=handle, **kwargs)

    def func(self, f):
        self.funcs.append(f)

    def one(self, key, day, start, end, hour=0):
        for item in self.items:
            value = lambda **x: item['handle'](item['query'](item['model'].objects(**x)))
            self.save('%s_%s' % (key, item['key']), value, day, start, end, hour, **item['kwargs'])
        for f in self.funcs:
            f(key, day, start, end, hour)

    def day(self, start_day):
        start = datetime.strptime(str(start_day).split(' ')[0], '%Y-%m-%d')
        end = datetime.strptime(str(start_day + timedelta(days=1)).split(' ')[0], '%Y-%m-%d')
        self.one('date', start_day.strftime('%Y-%m-%d'), start, end)

    def recent_week(self, start_day):
        start = datetime.strptime(str(start_day - timedelta(days=6)).split(' ')[0], '%Y-%m-%d')
        end = datetime.strptime(str(start_day + timedelta(days=1)).split(' ')[0], '%Y-%m-%d')
        self.one('recent_week', start_day.strftime('%Y-%m-%d'), start, end)

    def recent_month(self, start_day):
        start = datetime.strptime(str(start_day - timedelta(days=30)).split(' ')[0], '%Y-%m-%d')
        end = datetime.strptime(str(start_day + timedelta(days=1)).split(' ')[0], '%Y-%m-%d')
        self.one('recent_month', start_day.strftime('%Y-%m-%d'), start, end)

    def hour(self, now, day=True, by_week=True, by_month=True):
        start = now - timedelta(minutes=self.minutes)
        start = start - timedelta(minutes=start.minute, seconds=start.second,
                                    microseconds=start.microsecond)
        end = start + timedelta(hours=1)
        self.one('hour', start.strftime('%Y-%m-%d'), start, end, hour=start.hour)
        if day:
            self.day(start)
        if by_week:
            self.recent_week(start)
        if by_month:
            self.recent_month(start)


    def all(self):
        now = datetime.now()
        while now >= self.start:
            print('stats:', now)
            self.hour(now, day=now.hour == 0)
            now -= timedelta(hours=1)

    def run(self, mode='last', start=datetime(2018, 1, 1), minutes=1):
        self.start = start
        self.minutes = minutes

        if mode == 'last':
            start = time.time()
            print('stats start:', datetime.now())
            self.hour(datetime.now())
            print('stats takes:', time.time() - start)
        elif mode == 'all':
            self.all()

        # def run_stats(mode='last'):
        #     print('=====run_stats=====')
        #     if mode == 'last':
        #         start = time.time()
        #         print('stats start:', datetime.now())
        #         self.hour(datetime.now())
        #         print('stats takes:', time.time() - start)
        #     elif mode == 'all':
        #         self.all()

        # return run_stats


