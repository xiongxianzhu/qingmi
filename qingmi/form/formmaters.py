from html import escape, unescape
# 与上等效
# from xml.sax.saxutils import escape, unescape


__all__ = [
    'escape_data',
    'unescape_data',
]


def escape_data(data):
    """
    将数据里的字符串数据进行安全过滤， 防止XSS攻击
    :param data: 数据
    :return:
    """
    if isinstance(data, str):
        data = escape(data)
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = escape_data(value)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            data[index] = escape_data(item)
    return data


def unescape_data(data):
    """
    将数据里的字符串数据进行安全过滤， 防止XSS攻击
    :param data: 数据
    :return:
    """
    if isinstance(data, str):
        data = unescape(data)
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = unescape_data(value)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            data[index] = unescape_data(item)
    return data
