# coding: utf-8

from datetime import datetime, date, timedelta


def time2seconds(t):
    """ 时间转秒数 """
    """ t是字符串类型， 如'16:24:41' """
    h, m, s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)
    # return int(timedelta(hours=int(h),minutes=int(m),
    # seconds=int(s)).total_seconds())


def seconds2time(sec):
    """ 秒数转时间 """
    """ sec是整型， 如32399， sec取值范围是[0, 86399],
        对应的时间是'00:00:00'到'23:59:59'
    """
    if sec < 0 or sec > 86399:
        raise ValueError(
            'Invalid value: %s. The value interval of param sec is [0, 86399].' %
            sec)
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)
