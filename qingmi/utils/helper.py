# coding: utf-8
import string

# 造一个36进制： 'abcdefghijklmnopqrstuvwxyz0123456789'
case = string.ascii_lowercase + string.digits
# 造一个62进制： 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
case2 = string.ascii_uppercase + string.ascii_lowercase + string.digits


def get_uid(num, length=6):
    """ 
    根据用户索引生成用户的uid

    uid是由A-Z0-9共36个字符随机组成的指定长度的字符串

    num表示用户索引
        ...
        36的5次方为60466176，
        36的6次方为2176782336，
        ...

        按理说用户量不会超过2176782336，
        若num的起步基数为start，
        则num的取值范围为[start, 36**6-1].
    """
    res = []

    for i in range(length):
        res.append(case[num % 36])
        num //= 36
    return ''.join(reversed(res))


def get_uid2(num, length=4):
    """ 
    根据用户索引生成用户的uid

    uid是由A-Za-z0-9共62个字符随机组成的指定长度的字符串

    num表示用户索引
        ...
        62的3次方为238328，
        62的4次方为14776336，
        62的5次方为916132832，
        ...

        按理说用户量不会超过14776336，
        若num的起步基数为start，
        则num的取值范围为[start, 62**4-1].
    """
    res = []

    for i in range(length):
        res.append(case2[num % 62])
        num //= 62
    return ''.join(reversed(res))


def get_random_uid(num, length=4):
    """ 
    根据用户索引生成随机的用户的uid

    uid是由A-Za-z0-9共62个字符随机组成的指定长度的字符串

    num表示用户索引
        ...
        62的3次方为238328，
        62的4次方为14776336，
        62的5次方为916132832，
        ...

        按理说用户量不会超过14776336，
        若num的起步基数为start，
        则num的取值范围为[start, 62**4-1].
    """
    res = []
    random_case = case2

    for i in range(length):
        if i == 0:
            # 造一个62进制： 'RJSVfF3B0W5oEITjPCdZwaXxcDGHigrY7s92hQMbO4ykvUKlqmNzpuLe186Atn'
            # import random
            # case_list = list(case2)
            # random.shuffle(case_list)
            # ''.join((case_list))
            random_case = 'RJSVfF3B0W5oEITjPCdZwaXxcDGHigrY7s92hQMbO4ykvUKlqmNzpuLe186Atn'
        if i == 1:
            random_case = 'eF5t6zQl4gPCGUHrDakmKxA0WjcViE3qYRXvJZ7w29BNhSo18MLITundOyspbf'
        if i == 2:
            random_case = 'XEexkLIyqDrAMhcFOSYPuvVTQ7saCGnt61glNmw42JBRoKib3UHdj80WfpZ59z'
        if i == 3:
            random_case = 'ndgjiZxSbBV6eXzDoyrafHw9AU7PcJ34M2tRIvs5FEmYL8W1OTkq0uClhQpNKG'
        if i == 4:
            random_case = '8Zn9uxywWTreGV4oJQYvqKfdI6hUjkD1mLzC0t2Bb7POsagMXip5RSENc3HAlF'
        if i == 5:
            random_case = 'ftv9ZqNxYyURp0mbFBE47GCPO6nSVdJ5LAl1KWorkXjIh32gzHweTQi8DcMsua'
        if i == 6:
            random_case = 'XEexkLIyqDrAMhcFOSYPuvVTQ7saCGnt61glNmw42JBRoKib3UHdj80WfpZ59z'

        res.append(random_case[num % 62])
        num //= 62
    return ''.join(reversed(res))
