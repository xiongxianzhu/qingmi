# coding: utf-8

from datetime import datetime, date


def today():
    return datetime.strftime(str(date.today()), '%Y-%m-%d')

def parse_datetime(input):
    diff = datetime.now() - input
    if diff.days in [0, -1]:
        seconds = diff.days * 86400 + diff.seconds
        if seconds < -3600:
            return '%d小时后' % (-seconds // 3600)
        elif seconds < -60:
            return '%d分钟后' % (-seconds // 60)
        elif seconds < 0:
            return '%d秒后' % -seconds
        elif seconds < 60:
            return '%d秒前' % seconds
        elif seconds < 3600:
            return '%d分钟前' % (seconds // 60)
        else:
            return '%d小时前' % (seconds // 3600)
    elif diff.days < -365:
        return '%d年后' % (-diff.days // 365)
    elif diff.days < -30:
        return '%d个月后' % (-diff.days // 30)
    elif diff.days < -1:
        return '%d天后' % -(diff.days + 1)
    elif diff.days < 30:
        return '%d天前' % diff.days
    elif diff.days < 365:
        return '%d个月前' % (diff.days // 30)
    else:
        return '%d年前' % (diff.days // 365)
