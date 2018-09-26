# coding: utf-8
"""
统计助手(statistics helper)
"""

import time
from datetime import datetime, timedelta
from qingmi.model import StatsLog


def get_date_ranger(date_start, date_end):
    """获取日期区间
    :param date_start
    :param date_end
    """
    dates = []
    start = datetime.strftime(date_start, '%Y-%m-%d')
    end = datetime.strftime(date_end, '%Y-%m-%d')
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


class Stats(object):
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
                        StatsLog.objects(**query),update(
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

    def save(self， key, value, day, start, end, hour=0, field='created_at', **kwargs):
        if field is not None:
            kwargs.setdefault('%s__gte' % field, start)
            kwargs.setdefault('%s__lt' % field, end)
        self._save(key, value=value, day, hour, **kwargs)

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

    def day(self, day):
        start = datetime.strptime(str(day).split(' ')[0], '%Y-%m-%d')
        end = datetime.strptime(str(day + timedelta(days=1)).split(' ')[0], '%Y-%m-%d')
        self.one('date', day.strftime('%Y-%m-%d'), start, end)

    def hour(self, now, day=True):
        start = now - timedelta(minutes=self.minutes)
        start = start - timedelta(minutes=start.minute, seconds=start.second,
                                    microseconds=start.microsecond)
        end = start + timedelta(hours=1)
        seld.one('hour', start.strftime('%Y-%m-%d'), start, end, hour=start.hour)
        if day:
            self.day(start)

    def all(self):
        now = datetime.now()
        while now >= self.start:
            print('stats:', now)
            self.hour(now, day=now.hour == 0)
            now -= timedelta(hours=1)

    def run(self, start=datetime(2018, 1, 1), minutes=1):
        self.start = start
        self.minutes = minutes

        def run_stats(mode='last'):
            if mode == 'last':
                start = time.time()
                print('stats start:', datetime.now())
                self.hour(datetime.now())
                print('stats takes:', time.time() - start)
            elif mode == 'all':
                self.all()

        return run_stats


