import calendar
from datetime import datetime, date, timedelta


__all__ = [
    'today',
    'yesterday',
    'tomorrow',
    'oneday',
    'datetimeformat',
    'datetimeparse',
    'parse_datetime',
    'datetimeformat_from_timestamp',
    'datetime_from_timestamp',
    'get_datetime_ranger',
    'get_day_first_last_time',
    'get_month_first_last_time',
]


def today():
    """ 今天日期 """
    """ 返回datetime.datetime类型的日期，
        如今天是datetime.datetime(2018, 8, 22, 0, 0)，
        若序列化后为'2018-08-22 00:00:00'
    """
    return datetime.strptime(str(date.today()), '%Y-%m-%d')


def yesterday():
    """ 昨天日期 """
    """ 返回datetime.datetime类型的日期，
        如昨天是datetime.datetime(2018, 8, 21, 0, 0)，
        若序列化后为'2018-08-21 00:00:00'
    """
    today = date.today()
    diff_days = timedelta(days=1)
    yesterday = today - diff_days
    return datetime.strptime(str(yesterday), '%Y-%m-%d')


def tomorrow():
    """ 明天日期 """
    """ 返回datetime.datetime类型的日期，
        如明天是datetime.datetime(2018, 8, 21, 0, 0)，
        若序列化后为'2018-08-23 00:00:00'
    """
    today = date.today()
    diff_days = timedelta(days=1)
    tomorrow = today + diff_days
    return datetime.strptime(str(tomorrow), '%Y-%m-%d')


def oneday(days):
    """ A few days later/ago """
    if not isinstance(days, int):
        raise ValueError('Invalid int value for days: %s.' % days)
    today = date.today()
    diff_days = timedelta(days=days)
    oneday = today + diff_days
    return datetime.strptime(str(oneday), '%Y-%m-%d')


def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    """ 时间格式化成字符串 """
    return value.strftime(format)


def datetimeparse(value, format='%Y-%m-%d %H:%M:%S'):
    """ 时间格式化成datetime类型 """
    return datetime.strptime(value, format)


def parse_datetime(data):
    """ 格式化日期时间 """
    diff = datetime.now() - data
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


def datetimeformat_from_timestamp(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """ 时间戳转日期字符串 """
    return datetimeformat(datetime.fromtimestamp(timestamp), format)


def datetime_from_timestamp(timestamp):
    """ 时间戳转datetime类型 """
    return datetime.fromtimestamp(timestamp)


def get_datetime_ranger(start_time, end_time, seconds=300):
    """ 获取时间区间 """
    datetime_list = []
    start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    size = ((end - start).days * 24 * 3600 + (end - start).seconds) // seconds

    if size > 0:
        for i in range(size):
            datetime_list.append((
                start + timedelta(
                    seconds=i * seconds)).strftime('%Y-%m-%d %H:%M:%S'))
    return datetime_list


def get_day_first_last_time(current=None):
    """ 获取某天的第一个时间和最后一个时间

    传入一个时间， 获取该时间当天的第一个时间和最后一个时间， 精确到秒

    Parameters
    ----------
    current : {str}
        某天的任意时间， 格式为'%Y-%m-%d %H:%M:%S'， 如`2019-05-10 11:10:24`

    Return
    ----------
    first_time: {str}
        该天的第一时间， 格式为'%Y-%m-%d %H:%M:%S'， 如`2019-05-10 00:00:00`
    last_time: {str}
        该天的最后时间， 格式为'%Y-%m-%d %H:%M:%S'， 如`2019-05-10 23:59:59`
    """
    if not current:
        current = datetimeformat(today())
    dt_current = datetimeparse(current)

    year = dt_current.year
    month = dt_current.month
    day = dt_current.day

    dt_first_time = datetime(year=year, month=month, day=day)
    dt_last_time = datetime(year=year, month=month, day=day,
                            hour=23, minute=59, second=59)

    first_time = datetimeformat(dt_first_time)
    last_time = datetimeformat(dt_last_time)

    return first_time, last_time


def get_month_first_last_time(current=None):
    """ 获取某月的第一个时间和最后一个时间

    传入一个时间， 获取该时间月份的第一个时间和最后一个时间， 精确到秒

    Parameters
    ----------
    current : {str}
        某月的任意时间， 格式为'%Y-%m-%d %H:%M:%S'， 如`2019-05-10 11:10:24`

    Return
    ----------
    first_time: {str}
        该月的第一时间， 格式为'%Y-%m-%d %H:%M:%S'， 如`2019-05-01 00:00:00`
    last_time: {str}
        该月的最后时间， 格式为'%Y-%m-%d %H:%M:%S'， 如`2019-05-31 23:59:59`
    """
    if not current:
        current = datetimeformat(today())
    dt_current = datetimeparse(current)

    year = dt_current.year
    month = dt_current.month

    # 获取当月第一天的星期和当月的总天数
    first_day_week_day, month_range = calendar.monthrange(year, month)

    # 获取当月的第一时间和最后时间
    dt_first_time = datetime(year=year, month=month, day=1)
    dt_last_time = datetime(year=year, month=month, day=month_range,
                            hour=23, minute=59, second=59)

    first_time = datetimeformat(dt_first_time)
    last_time = datetimeformat(dt_last_time)

    return first_time, last_time
