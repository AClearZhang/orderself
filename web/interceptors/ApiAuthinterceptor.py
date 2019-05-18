# -*- coding: utf-8 -*-
from application import app
from flask import request, redirect, g, jsonify
from common.models.member.Member import Member
from common.libs.member.MemberService import MemberService

import re

'''
api拦截认证
'''
#装饰器  只去验证'/api' 的。验证用户是否已经登录。
@app.before_request
def before_request():
    api_ignore_urls = app.config['API_IGNORE_URLS']
    path = request.path   #获取页面的URL地址
    if '/api' not in path:
        return

    # cookie验证是否登陆过
    member_info = check_member_login()
    g.member_info = None
    if member_info:
        g.member_info = member_info

    # 那些不需要验证，是否登陆？？
    pattern = re.compile( '%s' % "|".join( api_ignore_urls ) )
    # app.logger.info("pattern: {}, path:{}".format( pattern, path ) )
    if pattern.match( path ):
        return

    if not member_info:
        resp = { 'code':-1, 'msg': '未登录，请先登录！', 'data':{} }
        return jsonify( resp )
    
    return #出错 return

'''
判断用户  是否已经登陆
'''
def check_member_login():
    auth_token = request.headers.get("Authorization")
  
    # 验证cookie 是否正确
    if auth_token is None:
        return False
    
    auth_info = auth_token.split("#")
    if len( auth_info ) != 2:
        return False
    
    try:
        member_info = Member.query.filter_by( id = auth_info[1] ).first()
    except Exception:
        return False
    
    if member_info is None:
        return False
    
    if auth_info[0] != MemberService.geneAuthCode( member_info ):               # 验证秘钥是否一致，一致则成功。不一致则返回！非法登录！
        return False


    return member_info
