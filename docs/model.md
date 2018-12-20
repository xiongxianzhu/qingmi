
# Model文档

#### 1. 用户日志-UserLog

属性 | 类型 | 必填 | 默认值 | 备注
:-|:-:|:-:|:-:|:-: 
id | ObjectId | 是 | | ID(mongodb自创建)
key | string(80) | 否 | | 键名
uid | string(80) | 否 | | 用户ID
log_type | string | 否 | 'ACTIVE' | 日志类型
useragent | string | 否 |  | 用户代理(UA)
ip | string(20) | 否 |  | IP
created_at | datetime | 是 | datetime.now | 创建时间
updated_at | datetime | 是 | datetime.now | 更新时间

`log_type`的值有：

- LOGIN='登录'
- LOGIN_ERROR='登录错误'
- LOGOUT='退出登录'
- REGISTER='注册'
- BIND_PHONE='绑定手机'
- BIND_EMAIL='绑定邮箱'
- UPDATE_PASSWORD='修改密码'
- RESET_PASSWORD='重置密码'
- IDCARD='实名认证'
- ACTIVE='活跃'

#### 2. 统计日志-StatsLog

属性 | 类型 | 必填 | 默认值 | 备注
:-|:-:|:-:|:-:|:-: 
id | ObjectId | 是 | | ID(mongodb自创建)
key | string(40) | 否 | | 键名
name | string(40) | 否 | | 名称
label | string(128) | 否 | | 标签
data_type | string(20) | 否 | | 类型
uid | string(128) | 否 | | 用户ID
xid | string(128) | 否 | | 其他ID
day | string(20) | 否 | | 日期(yyyy-MM-dd)
hour | int | 否 | 0 | 小时[0, 23] or [-1]
minute | int | 否 | 0 | 分钟[0, 59] or [-1]
value | Dynamic | 否 | | 值
created_at | datetime | 是 | datetime.now | 创建时间
updated_at | datetime | 是 | datetime.now | 更新时间

`data_type`的值有：

- INT='整数'
- FLOAT='浮点数'
- STRING='字符串'
- BOOLEAN='布尔值'


#### 3. 选项-Item

属性 | 类型 | 必填 | 默认值 | 备注
:-|:-:|:-:|:-:|:-: 
id | ObjectId | 是 | | ID(mongodb自创建)
name | string(40) | 否 |  | 名称
key | string(40) | 否 |  | 键名
data_type | string | 否 |  | 值类型
value | Dynamic | 否 |  | 值
created_at | datetime | 是 | datetime.now | 创建时间
updated_at | datetime | 是 | datetime.now | 更新时间

`data_type`的值有：

- INT='整数'
- FLOAT='浮点数'
- STRING='字符串'
- BOOLEAN='布尔值'

#### 4. 管理员-AdminUser

属性 | 类型 | 必填 | 默认值 | 备注
:-|:-:|:-:|:-:|:-: 
id | ObjectId | 是 | | ID(mongodb自创建)
uid | string(50) | 是 | | UID
username | string(20) | 是 |  | 用户名
password | string(50) | 否 |  | 密码
group | AdminGroup | 否 |  | 管理组
is_root | boolean | 否 | False | 是否超级管理员
active | boolean | 否 | True | 是否激活
freezed_at | datetime | 是 |  | 冻结时间
created_at | datetime | 是 | datetime.now | 创建时间
updated_at | datetime | 是 | datetime.now | 更新时间

#### 5. 管理组-AdminGroup

属性 | 类型 | 必填 | 默认值 | 备注
:-|:-:|:-:|:-:|:-: 
id | ObjectId | 是 | | ID(mongodb自创建)
name | string(40) | 是 |  | 组名
created_at | datetime | 是 | datetime.now | 创建时间
updated_at | datetime | 是 | datetime.now | 更新时间

#### 5. 管理员登录日志-AdminLoginLog

属性 | 类型 | 必填 | 默认值 | 备注
:-|:-:|:-:|:-:|:-: 
id | ObjectId | 是 | | ID(mongodb自创建)
user | AdminUser | 是 |  | 管理员
log_type | string | 是 |  | 类型
useragent | string | 否 |  | 用户代理(UA)
ip | string(20) | 否 |  | IP
created_at | datetime | 是 | datetime.now | 创建时间

`log_type`的值有：

- LOGIN='登录'
- LOGOUT='退出登录'
- ERROR='登录认证失败'

#### 6. 管理员操作日志-AdminChangeLog

属性 | 类型 | 必填 | 默认值 | 备注
:-|:-:|:-:|:-:|:-: 
id | ObjectId | 是 | | ID(mongodb自创建)
user | AdminUser | 是 |  | 管理员
log_type | string | 是 |  | 类型
model | string | 是 |  | 模块(如'User')
model_object_id | string | 是 |  | 模块对象ID
before_data | string | 是 |  | 操作前数据
after_data | string | 是 |  | 操作后数据
useragent | string | 否 |  | 用户代理(UA)
ip | string(20) | 否 |  | IP
created_at | datetime | 是 | datetime.now | 创建时间

`log_type`的值有：

- CREATE='创建'
- EDIT='编辑'
- DELETE='删除'
