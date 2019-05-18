
from flask import Blueprint, request, jsonify
from common.libs.Helper import ops_render, iPagination, getCurrentDate
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService
from common.models.User import User
from application import app, db
from sqlalchemy import or_

route_account = Blueprint( 'account_page', __name__)# 当前模块名称

@route_account.route("/index")
def index():
    resp_data = {}
    req = request.values
    page = int( req['page'] ) if ( 'page' in req and req['page'] ) else 1       # ???? page???
    query = User.query

    # 搜索功能
    if 'mix_kw' in req:
        # 进行  复合查询， 复杂的ORM查询方法
        rule = or_( User.nickname.ilike( "%{0}%".format( req['mix_kw'] ) ), User.mobile.ilike( "%{0}%".format( req['mix_kw'] ) ) )
        query = query.filter( rule )
    if 'status' in req and int( req['status'] ) > -1:
        query = query.filter( User.status ==  int( req['status'] ) )    # 有效无效/已删除的查询



    page_params = {
        "total": query.count(),
        "page_size": app.config['PAGE_SIZE'],
        "page": page,
        "display": app.config['PAGE_DISPLAY'],  # 想展示页数  页数太多的时候——进行半圆计算，from to进行展示
        "url": request.full_path.replace( "&page={}".format(page), "" )              # 此处不方便！ '/account/index'| 直接清空！
    }

    pages = iPagination( page_params )
    offset = ( page - 1 ) * app.config['PAGE_SIZE'] # 偏移量
    limit = app.config['PAGE_SIZE'] * page


    list = query.order_by( User.uid.desc() ).all()[ offset:limit ]      
    resp_data['list'] = list
    resp_data['pages']= pages
    # 优化 将搜索的字段放置在，input输入框提示栏当中
    resp_data['search_req'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']

    return ops_render("account/index.html", resp_data )

@route_account.route("/info")
def info():
    resp_data = {}
    req = request.values # request.args# 只是取“GET”方法的参数
    
    uid = int ( req['id'] )
#    app.logger.info( "req['id'] is :{}".format(req['id']) )

    reback_url = UrlManager.buildUrl("/account/index")
    if uid < 1:
         return redirect( reback_url )      # 错误处理

    info = User.query.filter_by( uid = uid ).first()
    if not info:
        return redirect( reback_url )

    resp_data['info'] = info


    return ops_render("account/info.html", resp_data)   # 传递到前段进行 传递

@route_account.route("/set", methods=['GET', 'POST'])
def set():
    default_pwd = "******"
    if request.method == "GET":
        # 判断 uid是否存在
        resp_data = {}
        req = request.args
        uid = int( req.get( "id", 0 ) )
        
        user_info = None
        if  uid:
            user_info = User.query.filter_by( uid = uid ).first()

        resp_data['user_info'] = user_info
        return ops_render( "account/set.html", resp_data )

    resp = { 'code': 200, 'msg': '操作成功~~', 'data':{} }
    req = request.values

    # 获取参数值 并 进行校验
    id = req['id'] if 'id' in req else ''
    nickname = req['nickname'] if 'nickname' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''
    email = req['email'] if 'email' in req else ''
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''    

    if nickname is None or len( nickname ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名"
        return jsonify( resp )
    if mobile is None or len( mobile ) < 11:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的手机号码"
        return jsonify( resp )
    if email is None or len( email ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱"
        return jsonify( resp )
    if login_name is None or len( login_name ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录用户名"
        return jsonify( resp )
    if login_pwd is None or len( login_pwd ) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录密码"
        return jsonify( resp )
    
    # 查询用户名是否 已经存在,而且 除去aclear本身！
    # 两种情况：1 修改 ;2 添加
    has_in = User.query.filter( User.login_name == login_name, User.uid != id ).first()
    if has_in:
        resp['code'] = -1
        resp['msg'] = "该用户名已存在，请换一个试试~"
        return jsonify( resp )

    # 写入数据库
    user_info = User.query.filter_by( uid = id ).first()
    if user_info:
        model_user = user_info                          # 编辑
    else:                                               # 新增
        model_user = User()
        model_user.create_time = getCurrentDate()
        model_user.login_salt =  UserService.geneSalt() # 加密密钥

    model_user.nickname = nickname
    model_user.mobile = mobile
    model_user.email = email
    model_user.login_name = login_name
    model_user.updated_time = getCurrentDate()

    if login_pwd != default_pwd:
        model_user.login_pwd = UserService.genePwd( login_pwd, model_user.login_salt )      # 注意login_pwd不同
    

    db.session.add( model_user )
    db.session.commit()
    return jsonify( resp )    


@route_account.route("/ops",methods=['POST'])
def ops():
    resp = { 'code': 200, 'msg': '操作成功~~', 'data':{} }
    req = request.values
    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试"
        return jsonify( resp )

    # 存在id
    user_info = User.query.filter_by( uid = id ).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "指定账号不存在~"
        return jsonify( resp )

    if act == "remove":
        user_info.status = 0
    elif act == "recover":
        user_info.status = 1

    user_info.updated_time = getCurrentDate()           # 提示一下再删除！
    db.session.add( user_info )
    db.session.commit()

    return jsonify( resp )