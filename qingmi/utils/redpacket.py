# coding: utf-8

"""
红包拆分
"""

import random
from decimal import Decimal


ZERO_VALUE = 'Zero Value of Param {}'
INVALID_VALUE = 'Invalid Value for Num: \'{}\''
TRIPLE_INVALID_VALUE = 'Invalid Value for Total-{}, Num-{}, Min-{}'


class Split(object):
    """ 红包拆分"""

    def decimal(self, value):
        """
        In [1]: Decimal(3.14)
        Out[1]: Decimal('3.140000000000000124344978758017532527446746826171875')
        In [2]: Decimal(str(3.14))
        Out[2]: Decimal('3.14')
        """
        return Decimal(str(value))

    def split_rmb_val(self, min, max):
        """ red packet money """
        return min if min > max else self.decimal(random.randint(min, max))

    def split_packet(self, total=0, num=0, min=0.01):
        """ split red pack """

        if not (total and num):
            raise ValueError(ZERO_VALUE.format('num' if total else 'total'))

        # Convert and Check of Total
        total = self.decimal(total)

        # Convert and Check of Num
        if isinstance(num, float) and int(num) != num:
            raise ValueError(INVALID_VALUE.format(num))
        num = self.decimal(int(num))

        # Convert and Check of Min
        min = self.decimal(min)

        # Compare Total and Num * Min
        if total < num * min:
            raise ValueError(TRIPLE_INVALID_VALUE.format(total, num, min))

        split_list = []
        for i in range(1, int(num)):
            # Random Safety High Limit Total
            safe_total = (total - (num - i) * min) / (num - i)
            split_val = self.split_rmb_val(min * 100, int(safe_total * 100)) / 100
            total -= split_val
            split_list.append(split_val)
        split_list.append(total)

        # Random Disarrange
        random.shuffle(split_list)

        return split_list
