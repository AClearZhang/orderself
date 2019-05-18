
from flask import Blueprint

route_api = Blueprint( 'api_page', __name__ )

''' 
会报404  因为在app 注册没有完全注册！Member方法
所以 此处需要全部注册进来！
'''
from web.controllers.api.Member import *
from web.controllers.api.Food import *
from web.controllers.api.Cart import *
from web.controllers.api.Order import *
from web.controllers.api.My import *
from web.controllers.api.Address import *


@route_api.route("/")
def index():
    return "Mina Api V1.0"

