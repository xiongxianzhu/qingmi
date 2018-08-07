# coding: utf-8

import random

def random_index(rate):
    """ 随机变量的概率函数 """
    #
    # 参数rate为list<int>
    # 返回概率事件的下标索引
    start = 0
    index = 0
    randnum = random.randint(0, sum(rate))

    for index, scope in enumerate(rate):
        start += scope
        if randnum < start:
            break
    return index

# def random_index(rate):
#     """ 随机变量的概率函数 """
#     #
#     # 参数rate为list<int>
#     # 返回概率事件的下标索引
#     start = 0
#     index = 0
#     randnum = random.randint(1, sum(rate))

#     for index, scope in enumerate(rate):
#         start += scope
#         if randnum <= start:
#             break
#     return index
