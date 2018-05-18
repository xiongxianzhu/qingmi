===============
qingmi
===============

Qingmi(青咪， 取自 ``情迷`` 谐音， 有 ``亲昵`` 之意)是一个基于Python3+Flask二次开发的应用层框架， 其内部封装了常用的模块和工具集， 主要用于针对flask web快速高效开发。

采用的技术栈：

- python3
- flask
- Werkzeug
- mongoengine
- celery
- fabric
- httpie
- Flask-Script
- Flask-WTF
- flask-mongoengine
- Flask-Login
- Flask-RESTful
- Flask-DebugToolbar
- Flask-Celery-Helper
- requests
- Flask-Caching
- Flask-Admin
- Flask-Uploads
- ipython
- Pillow
- click
- wheezy.captcha

功能特性：

- 管理后台
- 数据统计
- 短信发送
- 邮件发送
- 文件上传
- 验证码(图片验证码/短信验证码/邮箱验证码)
- 静态文件
- IP处理
- 日志
- 用户模块
- 角色模块
- 其他通用模块
- 权限管理
- 动态配置
- 定时任务(任务调度)
- 通用API(登录认证/获取token等)
- 第三方登录(QQ/微信/微博/github等)
- 第三方支付(支付宝/微信支付/京东支付/翼支付等)
- 部署(faric/rsync)
- 辅助工具(helper or utils, 加解密[hash/md5]/json/http/ip/日志/正则表达式/时间和日期/...)
- 单元测试

目录结构详解
==========

用法
====

测试
====

在有setup.py文件目录下， 执行 ``tox`` 命令可生成tox.ini文件。

::

    $ cd qingmi
    # Install tox
    $ sudo pip install tox
    # Run the test suites
    $ tox



文档
====


