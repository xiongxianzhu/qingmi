# coding: utf-8

import random
from datetime import datetime
from werkzeug.utils import cached_property
from qingmi.base import db
from qingmi.model import View
from qingmi.utils import get_ip, get_useragent


class AdminUser(db.Document):
    """ 管理员 """

    uid = db.IntField(verbose_name='UID')
    username = db.StringField(verbose_name='用户名')
    password = db.StringField(verbose_name='密码')
    group = db.ReferenceField('AdminGroup', verbose_name='管理组')
    is_root = db.BooleanField(default=False, verbose_name='超级管理员')
    is_active = db.BooleanField(default=True, verbose_name='激活')
    freezed_at = db.DateTimeField(verbose_name='冻结时间')
    logined_at = db.DateTimeField(default=datetime.now, verbose_name='登录时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='修改时间')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return '<AdminUser {username!r}>'.format(username=self.username)

    @property
    def is_authenticated(self):
        """ 是否登录 """
        return True

    @property
    def is_active(self):
        """ 是否激活 """
        return self.active

    @property
    def is_anonymous(self):
        """ 是否游客 """
        return False

    def get_id(self):
        return str(self.uid)


class AdminGroup(db.Document):
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

    def __repr__(self):
        return '<AdminGroup {name!r}>'.format(name=self.name)

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


class AdminLoginLog(db.Document):
    """ 管理后台登录日志 """

    TYPE = db.choices(LOGIN='登录', LOGOUT='退出登录', ERROR='登录认证失败')

    user = db.ReferenceField('AdminUser', verbose_name='用户')
    log_type = db.StringField(choices=TYPE.choices, verbose_name='类型')
    useragent = db.StringField(verbose_name='用户代理(UA)')
    ip = db.StringField(max_length=20, verbose_name='IP')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    @staticmethod
    def log(user, log_type, **kwargs):
        ua = kwargs.get('ua', get_useragent())
        ip = kwargs.get('ip', get_ip())
        AdminLoginLog(user=user, log_type=log_type, useragent=ua, ip=ip).save()

    @staticmethod
    def login(user):
        AdminLoginLog.log(user, AdminLoginLog.TYPE.LOGIN)

    @staticmethod
    def logout(user):
        AdminLoginLog.log(user, AdminLoginLog.TYPE.LOGOUT)

    @staticmethod
    def error(user):
        AdminLoginLog.log(user, AdminLoginLog.TYPE.ERROR)


class AdminChangeLog(db.Document):
    """ 管理后台操作日志 """

    TYPE = db.choices(CREATE='创建', EDIT='编辑', DELETE='删除')

    user = db.ReferenceField('AdminUser', verbose_name='用户')
    log_type = db.StringField(choices=TYPE.choices, verbose_name='类型')
    model = db.StringField(verbose_name='模块')
    before_data = db.StringField(verbose_name='操作前数据')
    after_data = db.StringField(verbose_name='操作后数据')
    useragent = db.StringField(verbose_name='用户代理(UA)')
    ip = db.StringField(max_length=20, verbose_name='IP')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    @staticmethod
    def log(user, log_type, model, before_data, after_data, **kwargs):
        ua = kwargs.get('ua', get_useragent())
        ip = kwargs.get('ip', get_ip())
        AdminChangeLog(user=user, log_type=log_type, model=model,
                        after_data=after_data, useragent=ua, ip=ip).save()

    @staticmethod
    def change_data(user, model, **kwargs):
        """ 变更数据 """
        before = dict(id=model.id)
        after = dict(id=model.id)
        if kwargs.get('form'):
            try:
                for k, v in kwargs.get('form').data.items():
                    if v != model[k]:
                        before[k] = model[k]
                        after[k] = v
            except:
                pass
        else:
            before = model.to_mongo()
        if kwargs.get('log_type') == AdminChangeLog.TYPE.DELETE:
            after = ''
        AdminChangeLog.log(
            user=user, log_type=kwargs.get('log_type'),
            model=model.__class__.__name__,
            before_data=str(before), after_data=str(after))

