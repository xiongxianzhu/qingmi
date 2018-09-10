# coding: utf-8

import random
from datetime import datetime
from werkzeug.utils import cached_property
from qingmi.base import db


class AdminUser(db.Document):
    """ 管理员 """

    uid = db.IntField(verbose_name='UID')
    username = db.StringField(verbose_name='用户名')
    password = db.StringField(verbose_name='密码')
    group = db.ReferenceField('Group', verbose_name='管理组')
    is_root = db.BooleanField(default=False, verbose_name='超级管理员')
    is_active = db.BooleanField(default=True, verbose_name='激活')
    freezed_at = db.DateTimeField(verbose_name='冻结时间')
    logined_at = db.DateTimeField(default=datetime.now, verbose_name='登录时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='修改时间')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return self.username

    def is_authenticated(self):
        """ 是否登录 """
        return True

    def is_active(self):
        """ 是否激活 """
        return self.active

    def is_anonymous(self):
        """ 是否游客 """
        return False

    def get_id(self):
        s = sign(current_app.config.get('SECRET_KEY'), password=self.password)
        return '{0}|{1}'.format(self.id, s)


class Group(db.Document):
    """ 管理组 """

    name = db.StringField(verbose_name='组名')
    power = db.ListField(db.ReferenceField('View'), verbose_name='使用权限')
    can_create = db.ListField(db.ReferenceField('View'), verbose_name='创建权限')
    can_edit = db.ListField(db.ReferenceField('View'), verbose_name='编辑权限')
    can_delete = db.ListField(db.ReferenceField('View'), verbose_name='删除权限')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='修改时间')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return self.name

    @cached_property
    def power_list(self):
        return [x.name for x in self.power]

    @cached_property
    def can_create_list(self):
        return [x.name for x in self.can_create]

    @cached_property
    def can_edit_list(self):
        return [x.name for x in self.can_edit]

    @cached_property
    def can_delete_list(self):
        return [x.name for x in self.can_delete]