# coding: utf-8
import string

# 造一个36进制： 'abcdefghijklmnopqrstuvwxyz0123456789'
case = string.ascii_lowercase + string.digits

def get_uid(num):
    """ 
    根据用户索引生成用户的uid

    num表示用户索引
        ...
        36的5次方为60466176，
        36的6次方为2176782336，
        ...

        按理说用户量不会超过2176782336，
        若num的起步基数为start，
        则num的取值范围为[0, 36**6-1-start].
    """
    res = []

    for i in range(6):
        res.append(case[num % 36])
        num //= 36
    return ''.join(reversed(res))
