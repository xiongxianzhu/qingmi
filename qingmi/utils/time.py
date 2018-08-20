# coding: utf-8


def time2seconds(t):
    """ 时间转秒数 """
    h, m, s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def seconds2time(sec):
    """ 秒数转时间 """
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)
