# coding: utf-8
"""
Default qingmi settings.
"""

import os

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(ROOT, 'data')
FONT_ROOT = os.path.join(DATA_ROOT, 'fonts')

DEBUG = False

# People who get code error notifications.
# In the format [('Full Name', 'email@example.com'), ('Full Name',
# 'anotheremail@example.com')]
ADMINS = []
