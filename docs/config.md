# config根目录配置文件变更记录
## 原因
由于文件中 有自己密码等重要信息,不得以删除对应配置文件。

## 用户需添加
### /config/base_setting.py
```python
# -*- coding: utf-8 -*-
# 此处为共用的，  数据库费巩勇
DEBUG = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = 'mysql://root:your key@127.0.0.1/food_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

APP = {
    'domain': 'your domain'
}

SERVER_PORT = 8999          # 共用的！
AUTH_COOKIE_NAME = "your auth name"

SEO_TITLE="自助点餐系统"
# 过滤URL
IGNORE_URLS = [
    "^/user/login",             # 判断登录，但是如果未登录。也是没问题的
]

IGNORE_CHECK_LOGIN_URLS = [
    "^/static",                 # 完全不判断登录
    "^/favicon.ico"
]
# Api过滤URL
API_IGNORE_URLS = [
    "^/api"                     # 新增过滤规则， 过滤掉以 /api 开头的拦截器！！！
]

# 分页设置
PAGE_SIZE = 50                 # 设置分页/每一页50记录
PAGE_DISPLAY = 5                # 分页页码 显示数目


STATUS_MAPPING = {
    "1": "正常",
    "0": "已删除"
}


MINA_APP = {
    'appid': 'your id',
    'appkey': 'your key'
}

UPLOAD = {
    'ext': [ 'jpg', 'gif', 'bmp', 'jpeg', 'png' ],
    'prefix_path': '/web/static/upload/',                    # 上传文件前缀/ 内部需要完全的前缀
    'prefix_url': '/static/upload/'                          # 配置文件获取/ 而外部的访问  html只需要前缀简称-获得上传文件夹；因为拦截器的功效
}

# 仅仅是 支付状态
PAY_STATUS_MAPPING = {
    "-8": "待支付",
    "1": "已支付",
    "0": "已关闭",
}

'''
    映射 order_list.js的前端
    statusType: ["待付款", "待发货", "待收货", "待评价", "已完成","已关闭"],
    status:[ "-8","-7","-6","-5","1","0" ],

    此处为给web后台用
'''
PAY_STATUS_DISPLAY_MAPPING = {
    "0": "订单关闭",
    "1": "订单完成",
    "-5": "待评价",
    "-6": "待收货",
    "-7": "待审核",
    "-8": "待支付",
}

'''
    商家自用 cat_id映射
    banner映射—— 库存代表 推荐id位置
    二维码 映射
'''
SHOP_USING = {
    "cat_id": "your shoper id",
    "erweima_id": "your id",
    "tele_phone": "your phone",
}
```
### /config/local_setting.py
```python
# -*- coding: utf-8 -*-
DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'mysql://root:your key@127.0.0.1/food_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf8mb4"

```
### /config/production_setting.py
```python
# -*- coding: utf-8 -*-
DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'mysql://root:your key@127.0.0.1:your port/food_db?charset=utf8mb4'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf8mb4"

APP = {
    'domain':'your domain'
}

RELEASE_VERSION="your version"

```

