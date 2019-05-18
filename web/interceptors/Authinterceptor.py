# -*- coding: utf-8 -*-
from application import app
from flask import request, redirect, g
from common.models.User import User
from common.libs.user.UserService import UserService
from common.libs.UrlManager import UrlManager
import re


#装饰器  除了'api' 的都验证！
@app.before_request
def before_request():
    # 登录页面不用进行拦截！ 正则表达式
    # static 和 用户登录界面 是不需要登陆的
    ignore_urls = app.config['IGNORE_URLS']
    ignore_check_login_urls = app.config['IGNORE_CHECK_LOGIN_URLS']
#    app.logger.info("ignore_urls: {}, ignore_check_login_urls:{}".format(ignore_urls, ignore_check_login_urls ) )

    path = request.path   #获取页面的URL地址

    pattern = re.compile( '%s' % "|".join( ignore_check_login_urls ) )
#    app.logger.info("pattern: {}, path:{}".format( pattern, path ) )
    if pattern.match( path ):
        return


    if '/api' in path:
        return 

    # cookie验证是否登陆过
    user_info = check_login()
    g.current_user = None
    if user_info:
        g.current_user = user_info


    pattern = re.compile( '%s' % "|".join( ignore_urls ) )
    if pattern.match( path ):
        return

    if not user_info:
        return redirect( UrlManager.buildUrl("/user/login") )
    return #出错 return

'''
判断用户  是否已经登陆
'''
def check_login():
    cookies = request.cookies
    auth_cookie = cookies[ app.config['AUTH_COOKIE_NAME'] ] if app.config['AUTH_COOKIE_NAME'] in cookies else ''
    # app.logger.info( auth_cookie )
    # 验证cookie 是否正确
    if auth_cookie is None:
        return False
    
    auth_info = auth_cookie.split("#")
    if len( auth_info ) != 2:
        return False
    
    try:
        user_info = User.query.filter_by( uid = auth_info[1] ).first()
    except Exception:
        return False
    
    if user_info is None:
        return False
    
    if auth_info[0] != UserService.geneAuthCode( user_info ):
        return False


    return user_info
