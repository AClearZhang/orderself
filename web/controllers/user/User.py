from flask import Blueprint, request, jsonify,make_response,redirect,g
import json
from common.models.User  import User
from common.libs.user.UserService  import UserService
from application import app, db
from common.libs.UrlManager import UrlManager
from common.libs.Helper import ops_render

route_user = Blueprint( 'user_page', __name__)# 当前模块名称

@route_user.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == "GET":
        return ops_render("user/login.html")
    

    resp = { 'code' : 200, 'msg' : '登陆成功' }                         # 返回相应的 Json数值
    req = request.values
    login_name = req['login_name'] if 'login_name' in req else ' '
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ' '

    # 输入有效性判断
    if login_name is None or len( login_name ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入正确的用户名."
        return jsonify( resp )
    if login_pwd is None or len( login_pwd ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入正确的用户密码."
        return jsonify( resp )

    # 数据库查找用户名
    # 数据库使用login_salt 秘钥进行密码加密验证登录！
    user_info = User.query.filter_by( login_name = login_name ).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = '请输入正确的登录用户名或密码！'
        return jsonify( resp )
    if user_info.login_pwd != UserService.genePwd( login_pwd, user_info.login_salt ):
        resp['code'] = 1
        resp['msg'] = '请输入正确的登录用户名或密码！'
        return jsonify( resp )

    # cookie验证
    # response = make_response( json.dumps( resp ) )
    response = make_response( jsonify( resp ) )
    response.set_cookie( app.config['AUTH_COOKIE_NAME'], "%s#%s"%( UserService.geneAuthCode( user_info ), user_info.uid ) )#前一个 %S是 cookie的加密的过程. 

    # return jsonify( resp )
    return response

    # return "login_name:{} -  login_pwd:{}.".format(login_name, login_pwd)


@route_user.route("/edit", methods=["GET","POST"])
def edit():
    if request.method == "GET":
        return ops_render("user/edit.html", { 'current': 'edit' })
  

    # 一下为POST方法的处理过程
    resp = { 'code': '200', 'msg': '操作成功~', 'data':{} }
    req = request.values
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req['email'] if 'email' in req else ''

    if nickname is None or len( nickname ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名~"
        return jsonify( resp )
        
    if email is None or len( email ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱~"
        return jsonify( resp )

    # 修改对应user_info  进行提交
    user_info = g.current_user
    user_info.nickname = nickname
    user_info.email = email

    db.session.add( user_info )
    ad.session.commit()
    return jsonify( resp )

@route_user.route("/reset-pwd", methods=['GET', 'POST'])
def resetPwd():
    if request.method == "GET":
        return ops_render("user/reset_pwd.html", { 'current': 'reset-pwd' })

    user_info = g.current_user
    # 以下为POST方法的处理过程
    resp = { 'code': '200', 'msg': '操作成功~', 'data':{} }
    req = request.values
    
    old_password = req['old_password'] if 'old_password' in req else ''
    new_password = req['new_password'] if 'new_password' in req else ''

    login_pwd = UserService.genePwd( old_password, user_info.login_salt )
    # 参数有效性判断
    if old_password is None or len( old_password ) < 6 or login_pwd != user_info.login_pwd:
        resp['code'] = -1
        resp['msg'] = "抱歉！原始密码错误，请重新输入！"
        app.logger.info( "login_pwd is :{} old_password is :{}".format(login_pwd, old_password ) )
        return jsonify( resp )
        
    if new_password is None or len( new_password ) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的新密码~"
        return jsonify( resp )

    if new_password == old_password:
        resp['code'] = -1
        resp['msg'] = "新密码和原始密码不能相同！请重新输入一个！"
        return jsonify( resp )

    # 修改对应user_info  进行提交
    user_info.login_pwd = UserService.genePwd( new_password, user_info.login_salt )

    db.session.add( user_info )
    db.session.commit()
    
    # 注意进行cookie的刷新
    # response = make_response( json.dumps( resp ) )
    response = make_response( jsonify( resp ) )
    response.set_cookie( app.config['AUTH_COOKIE_NAME'], "%s#%s"%( UserService.geneAuthCode( user_info ), user_info.uid ) )#前一个 %S是 cookie的加密的过程. 

    return response

    


# 登出功能——直接清空 cookie
@route_user.route("/logout")
def logout():
    response = make_response( redirect( UrlManager.buildUrl("/user/login") ) )
    response.delete_cookie( app.config['AUTH_COOKIE_NAME'] )
    return response
