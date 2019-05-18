# -*- coding: utf-8 -*-
# 会员入口文件, 得到会员信息  进行处理
'''
小程序 api前台用户登录界面
'''
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app, db
import requests, json
from common.models.member.Member import Member
from common.models.member.OauthMemberBind import OauthMemberBind
from common.libs.Helper import getCurrentDate
from common.libs.member.MemberService import MemberService
from common.models.food.WxShareHistory import WxShareHistory

@route_api.route("/member/login", methods=['GET', 'POST'])
def login():
    resp = { 'code': 200, 'msg': '操作成功~', 'data': {} }
    req = request.values
    app.logger.info( req )
    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "授权用户code失败！"
        return jsonify( resp )

    # # 下面通过code 获取用户的一些基本信息，以及+ appid  获得用户唯一的openid标致！
    # # 方便进行  用户是否已经注册的！  数据库比照的判定！所以会员 一定要有自己的数据库!
    # # 发送 get请求
    # url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code".format( app.config['MINA_APP']['appid'], app.config['MINA_APP']['appkey'], code)  
    # # 安装request扩展
    # r = requests.get( url )
    # res = json.loads( r.text )
    # app.logger.info( "The result RES is:{0} and The result R.Text is:{1} ".format( res, r.text ))
    # openid = res['openid']                  # 获取用户唯一表示 
    
    openid = MemberService.getWeChatOpenid(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        return jsonify( resp )


    # 区别前端请求 和  后端向微信服务器的 openid的  进行的请求.
    nickname = req['nickName'] if 'nickName' in req else ''
    sex = req['gender'] if 'gender' in req else 0
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''

    '''
        判断用户是否已经  注册过
    '''
    bind_info = OauthMemberBind.query.filter_by( openid = openid, type = 1 ).first()
    if bind_info:                           # 已经注册过
        member_info = Member.query.filter_by( id = bind_info.member_id ).first()
        # resp['code'] = -1
        resp['msg'] = "抱歉！您已绑定"
        #resp['data'] = { 'nickname': member_info.nickname }
        # 产生 token 表明已经绑定了！
        token = "%s#%s"%( MemberService.geneAuthCode( member_info ), member_info.id )
        resp['data'] = { 'token': token }
        return jsonify( resp )

    # 数据库中没有： 则进行注册  并写入数据库
    model_member = Member()
    model_member.nickname = nickname
    model_member.sex = sex
    model_member.avatar = avatar
    model_member.salt = MemberService.geneSalt()
    # model_member.updated_time = getCurrentDate()                # 不好修改为：
    model_member.updated_time = model_member.created_time = getCurrentDate()
    db.session.add( model_member )
    db.session.commit()

    # app.logger.info( res + "\n\ntest" + "\b\n分行 进行式！" )

    model_bind = OauthMemberBind()
    model_bind.member_id = model_member.id
    model_bind.type = 1
    model_bind.openid = openid
    model_bind.extra = ''
    model_bind.updated_time = model_bind.created_time = getCurrentDate()
    db.session.add( model_bind )
    db.session.commit()
    #resp['data'] = { 'nickname': nickname }                  # 注意此处重复了！————所以可以进行代码的优化操作！
                                                             # 代码优化———— 当用户注册之后  不需要再首先进入 带登录界面！
     # 产生 token 表明已经绑定了！
    token = "%s#%s"%( MemberService.geneAuthCode( member_info ), member_info.id )
    resp['data'] = { 'token': token }
    return jsonify( resp )                                   # 必须有 json的返回数据！因为 有request。否则会报 500/300错误



@route_api.route("/member/check-reg", methods=['GET', 'POST'])
def checkReg():
    resp = { 'code': 200, 'msg': '操作成功~', 'data': {} }
    req = request.values
    code = req['code'] if 'code' in req else ''
    if not code or len( code )<-1:
        resp['code'] = -1
        resp['msg'] = "需要code"
        return jsonify( resp )
    
    openid = MemberService.getWeChatOpenid( code )
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        return jsonify( resp )

    # 查看是否 绑定关系openid 已有
    bind_info = OauthMemberBind.query.filter_by( openid = openid, type = 1 ).first()
    if bind_info is None:
        resp['code'] = -1
        resp['msg'] = "未绑定"
        return jsonify( resp )    

    member_info = Member.query.filter_by( id = bind_info.member_id ).first()
    if member_info is None:
        resp['code'] = -1
        resp['msg'] = "未查询到绑定信息"
        return jsonify( resp )    

    # 产生 token 表明已经绑定了！
    token = "%s#%s"%( MemberService.geneAuthCode( member_info ), member_info.id )
    resp['data'] = { 'token': token }
    return jsonify( resp )                                   # 必须有 json的返回数据！因为 有request。否则会报 500/300错误

'''
哪一个用户  分享了哪一个物品，记录下来。
方便进行分享的统计
'''

@route_api.route("/member/share", methods=['POST'])
def memberShare():
    resp = { 'code': 200, 'msg': '操作成功~', 'data': {} }
    req = request.values
    url = req['url'] if 'url' in req else ''
    member_info = g.member_info             # 注意！！！
    # 存入数据库
    model_share = WxShareHistory()
    
    if member_info:
        model_share.member_id = member_info.id

    model_share.share_url = url
    model_share.created_time = getCurrentDate()
    db.session.add( model_share )
    db.session.commit()

    return jsonify( resp )

'''
    my 获取用户信息
'''
@route_api.route( '/member/info' )
def memberInfo():
    resp = { 'code': 200, 'msg': '操作成功~', 'data': {} }
    member_info = g.member_info
    resp['data']['info'] = {
        "nickname": member_info.nickname,
        "avatar_url": member_info.avatar,
        "sex": member_info.sex,
    }

    return jsonify( resp )


