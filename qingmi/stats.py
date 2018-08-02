# coding: utf-8
"""
统计助手(statistics helper)
"""

import time
from datetime import datetime, timedelta
from qingmi.model import StatsLog


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

    def save(self， key, value, day, start, end, hour=0, field='updated_at', **kwargs):
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
        self.stats(key, model, **kwargs)

    def sum(self, key, model, sub, **kwargs):
        self.stats(key, model, query=lambda x: x.aggregate_sum(sub), **kwargs)

    def distinct(self, key, model, sub, **kwargs):
        self.stats(key, model, query=lambda x: x.distinct(sub), handle=len, **kwargs)

    def aggregate(self):
        pass

    def func(self, f):
        self.funcs.append(f)

    def one(self, key, day, start, end, hour=0):
        pass

    def hour(self, now, day=True):
        pass

    def all(self):
        pass

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


