# -*- coding: utf-8 -*-
from application import app


'''
统一拦截器
'''
from web.interceptors.Authinterceptor import *
from web.interceptors.ApiAuthinterceptor import *


'''
蓝图功能  对所有的页面进行蓝图功能的配置.
'''
from web.controllers.index import route_index
from web.controllers.user.User  import route_user
from web.controllers.static import route_static
from web.controllers.account.Account import route_account
from web.controllers.finance.Finance import route_finance
from web.controllers.food.Food import route_food
from web.controllers.member.Member import route_member
from web.controllers.stat.Stat import route_stat
from web.controllers.api import route_api                           # 默认是访问 __init__
from web.controllers.upload.Upload import route_upload                           # 默认是访问 __init__
from web.controllers.chart import route_chart                           # 默认是访问 __init__


app.register_blueprint( route_index, url_prefix="/" )
app.register_blueprint( route_user, url_prefix = "/user" )
app.register_blueprint( route_static, url_prefix = "/static" )
app.register_blueprint( route_account, url_prefix = "/account" )
app.register_blueprint( route_finance, url_prefix = "/finance" )
app.register_blueprint( route_food, url_prefix = "/food" )
app.register_blueprint( route_member, url_prefix = "/member" )
app.register_blueprint( route_stat, url_prefix = "/stat" )
app.register_blueprint( route_api, url_prefix = "/api" )
app.register_blueprint( route_upload, url_prefix = "/upload" )
app.register_blueprint( route_chart, url_prefix = "/chart" )

