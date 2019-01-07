from datetime import datetime, date, timedelta


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
    if type(days) != int:
        raise ValueError('Invalid int value for days: %s.' % days)
    today = date.today() 
    diff_days = timedelta(days=days)
    oneday = today + diff_days  
    return datetime.strptime(str(oneday), '%Y-%m-%d')

def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    """ 时间格式化 """
    return value.strftime(format)

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
