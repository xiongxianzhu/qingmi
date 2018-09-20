# coding: utf-8

import random
from datetime import datetime
from werkzeug.utils import cached_property
from qingmi.base import db, bcrypt
from qingmi.utils import get_ip, get_useragent


class AdminUser(db.Document):
    """ 管理员 """

    uid = db.StringField(max_length=50, verbose_name='UID')
    username = db.StringField(max_length=50, verbose_name='用户名')
    password = db.StringField(max_length=128, verbose_name='密码')
    group = db.ReferenceField('AdminGroup', verbose_name='管理组')
    is_root = db.BooleanField(default=False, verbose_name='是否超级管理员')
    active = db.BooleanField(default=True, verbose_name='是否激活')
    freezed_at = db.DateTimeField(verbose_name='冻结时间')
    logined_at = db.DateTimeField(default=datetime.now, verbose_name='登录时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    meta = dict(
        ordering=['-created_at'],
    )

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
        return str(self.username)

    def hash_password(self, password):
        """ hash算法加密密码 """
        # 在python3中，你需要使用在generate_password_hash()上使用decode('utf-8')方法
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """ 验证密码 """
        return bcrypt.check_password_hash(self.password, password)


class AdminGroup(db.Document):
    """ 管理组 """

    name = db.StringField(max_length=50, verbose_name='组名')
    power = db.ListField(db.ReferenceField('View'), verbose_name='使用权限')
    can_create = db.ListField(db.ReferenceField('View'), verbose_name='创建权限')
    can_edit = db.ListField(db.ReferenceField('View'), verbose_name='编辑权限')
    can_delete = db.ListField(db.ReferenceField('View'), verbose_name='删除权限')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')
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


class View(db.Document):
    """ 视图 """

    TYPE = db.choices(DEFAULT='默认', MODEL='模型', CATEGORY='分类')

    name = db.StringField(max_length=128, verbose_name='名称')
    desc = db.StringField(max_length=128, verbose_name='描述')
    view_type = db.StringField(default=TYPE.DEFAULT, choices=TYPE.CHOICES,
                                verbose_name='类型')
    # model = db.ReferenceField('Model', verbose_name='模型')
    menu_icon = db.StringField(max_length=128, verbose_name='图标')
    page_size = db.IntField(default=50, verbose_name='每页记录数')
    can_create = db.BooleanField(default=True, verbose_name='允许创建')
    can_edit = db.BooleanField(default=True, verbose_name='允许编辑')
    can_delete = db.BooleanField(default=True, verbose_name='允许删除')
    can_view_details = db.BooleanField(default=False, verbose_name='允许查看详情')
    can_export = db.BooleanField(default=False, verbose_name='允许导出')
    # column_list = db.ListField(db.StringField(), verbose_name='显示列表字段')
    # column_exclude_list = db.ListField(db.StringField(), verbose_name='隐藏列表字段')
    column_center_list = db.ListField(db.StringField(), verbose_name='居中列表')
    created_at = db.DateTimeField(default=datetime.now, verbose_name='创建时间')
    updated_at = db.DateTimeField(default=datetime.now, verbose_name='更新时间')

    def __repr__(self):
        return '<View {name!r}>'.format(name=self.name)

    def __unicode__(self):
        return self.name


class AdminLoginLog(db.Document):
    """ 管理员登录日志 """

    TYPE = db.choices(LOGIN='登录', LOGOUT='退出登录', ERROR='登录认证失败')

    user = db.ReferenceField('AdminUser', verbose_name='用户')
    log_type = db.StringField(choices=TYPE.CHOICES, verbose_name='类型')
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
    """ 管理员操作日志 """

    TYPE = db.choices(CREATE='创建', EDIT='编辑', DELETE='删除')

    user = db.ReferenceField('AdminUser', verbose_name='用户')
    log_type = db.StringField(choices=TYPE.CHOICES, verbose_name='类型')
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
                        before_data=before_data, after_data=after_data,
                        useragent=ua, ip=ip).save()

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
            user=user,
            log_type=kwargs.get('log_type'),
            model=model.__class__.__name__,
            before_data=str(before),
            after_data=str(after),
        )

    @staticmethod
    def ajax_change(user, model, **kwargs):
        before_data = dict(id=kwargs.get('id'))
        after_data = dict(id=kwargs.get('id'))
        key = kwargs.get('key')
        before_data[key] = kwargs.get('before_data')
        after_data[key] = kwargs.get('after_data')

        AdminChangeLog.log(
            user=user,
            model=model.__name__,
            before_data=str(before_data),
            after_data=str(after_data),
            log_type=AdminChangeLog.TYPE.EDIT,
        )