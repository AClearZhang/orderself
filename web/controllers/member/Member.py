# -*- coding: utf-8 -*-
'''
    会员列表  后台查看Member的列表
'''
from flask import Blueprint, request, redirect,  jsonify
from application import app, db
from common.libs.UrlManager import UrlManager
from common.libs.Helper import ops_render, iPagination, getCurrentDate,\
                                     selectFilterObj, getDictFilterField, selectCommentFoodIDs
from common.models.member.Member import Member
from common.models.member.MemberComments import MemberComments
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
route_member = Blueprint( 'member_page',__name__ )

@route_member.route( "/index" )
def index():
    resp_data = {}
    
    req = request.values
    page = int( req['page'] ) if ( 'page' in req and req['page'] )  else 1
    query = Member.query                                            # 封装

    # get 混合查询添加
    if 'mix_kw' in req:
        query = query.filter( Member.nickname.ilike("%{0}%".format(req['mix_kw'] )) )# 忽略大小写 ilike

    if 'status' in req and int( req['status'] > -1 ):                   # 状态查询添加
        query = query.filter( Member.status == int( req['status'] ) )  # 注意查询是在这，所以在进行 搜索时，要标记状态.方便好用！

    # 开始分页
    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={0}".format(page),  "")
    }

    pages = iPagination( page_params )
    offset = ( page - 1 ) * app.config['PAGE_SIZE']

    list = query.order_by( Member.id.desc() ).offset( offset ).limit( app.config['PAGE_SIZE'] ).all()

    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['current'] = 'index'   
    resp_data['search_con'] = req   
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']   
    return ops_render( "member/index.html", resp_data )

# @route_member.route( "/info" )
# def info():
#     # 获取用户信息，并进行展示
#     resp_data = {}
#     req = request.args
#     id = int ( req.get( "id", 0) )
    
#     reback_url = UrlManager.buildUrl("/member/index")
#     if id < 1:
#         return redirect( reback_url )

#     info = Member.query.filter_by( id = id ).first()
#     if not info:
#         return redirect( reback_url )
    
#     resp_data['info'] = info
#     resp_data['current'] = 'index'

#     return ops_render( "member/info.html", resp_data )

@route_member.route( "/info" )
def info():
    resp_data = {}
    req = request.args
    id = int( req.get( "id",0 ) )
    reback_url = UrlManager.buildUrl( "/member/index" )
    if id < 1:
        return redirect( reback_url )

    info = Member.query.filter_by( id =id ).first()
    if not info:
        return redirect( reback_url )

    pay_order_list = PayOrder.query.filter_by( member_id = id ).filter( PayOrder.status.in_( [-8,1] ) )\
        .order_by( PayOrder.id.desc() ).all()
    comment_list = MemberComments.query.filter_by( member_id = id ).order_by( MemberComments.id.desc() ).all()

    resp_data['info'] = info
    resp_data['pay_order_list'] = pay_order_list
    resp_data['comment_list'] = comment_list
    resp_data['current'] = 'index'
    return ops_render( "member/info.html",resp_data )

@route_member.route( "/set" , methods=["GET", "POST"])
def set():
    if request.method == "GET":
        resp_data = {}
        req = request.args
        id = int ( req.get( "id", 0) )
        reback_url = UrlManager.buildUrl("/member/index")
        if id < 1:
            return redirect( reback_url )
        
        info = Member.query.filter_by( id = id ).first()
        if not info:
            return redirect( reback_url )
        
        resp_data['info'] = info
        resp_data['current'] = 'index'                  # 当前栏目——高亮的光标 index
        return ops_render( "member/set.html", resp_data )


    resp = { 'code': 200, 'msg': '操作成功~', 'data':{} }
    req = request.values
    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    if nickname is None or len( nickname ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名"
        return jsonify( resp )

    member_info = Member.query.filter_by( id = id ).first()

    if member_info.status != 1:
        resp['code'] = -1
        resp['msg'] = "删除状态，不允许编辑。"
        return jsonify( resp )

    if not member_info:
        resp['code'] = -1
        resp['msg'] = "指定的会员不存在~"
        return jsonify( resp )

    # 如果存在：
    member_info.nickname = nickname
    member_info.updated_time = getCurrentDate()
    db.session.add( member_info )
    db.session.commit()
    return jsonify( resp )


'''
    返回用户评论
    <th>头像</th>
    <th>姓名</th>
    <th>美餐</th>
    <th>评论内容</th>
    <th>打分</th>
    [  
        {
            member_info:{ id, avatar, nickname },
            foods:[ {id name }, {}, {} ],
            content: ,
            score: ,
        },
        {
            member_info:{ id, avatar, nickname },
            ……

        }

    ]
    member_info
    foods
    content
    score
'''
# 修改
@route_member.route( "/comment" )
def comment():
    resp_data = {}
    req = request.values
    page = int( req['page'] ) if ( 'page' in req and req['page'] )  else 1
    query = MemberComments.query

    # 开始分页
    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={0}".format(page),  "")
    }

    pages = iPagination( page_params )
    offset = ( page - 1 ) * app.config['PAGE_SIZE']
    # 查找 分页评论表
    comment_list = query.order_by(MemberComments.member_id.asc()).offset( offset ).limit( app.config['PAGE_SIZE'] ).all()
    # 待完成     selectFilterObj
    

    data_comment_list = []
    if comment_list:
        # 寻找foods_id
        foods_id = selectCommentFoodIDs( comment_list, 'food_ids' )
        foods_map = getDictFilterField( Food, Food.id, 'id', foods_id )
        # print( "foods_id:{0} foods_map:{1}".format( foods_id, foods_map) )
        # 寻找 member_id
        member_ids = selectFilterObj( comment_list, 'member_id' )
        member_ids_map = getDictFilterField( Member, Member.id, 'id', member_ids )
        # print( "member_ids:{0} member_ids_map:{1}".format( member_ids, member_ids_map) )

        # pay_order_ids = selectFilterObj( comment_list,"pay_order_id" )
        # pay_order_map = getDictFilterField( PayOrder,PayOrder.id,"id",pay_order_ids )
        for item in comment_list:
            tmp_member_info = member_ids_map[ item.member_id ]
            data_foods = []
            for i in item.food_ids.split('_'):
                if i != '':
                    data_foods.append( foods_map[ int(i) ] )

            tmp_data = {
                "member_info": tmp_member_info,
                "foods": data_foods,
                "content":item.content,
                "score":item.score,
                "date":item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            data_comment_list.append( tmp_data )
    resp_data['list'] = data_comment_list
    resp_data['pages'] = pages
    resp_data['current'] = 'comment'   
    return ops_render( "member/comment.html", resp_data )


@route_member.route( "/ops", methods=['POST'] )
def ops():
    resp = { 'code': 200, 'msg': '操作成功~', 'data':{} }
    req = request.values
    id = req['id']  if 'id' in req else 0
    act = req['act']  if 'act' in req else ''
    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择要操作的账号~~"
        return jsonify( resp )
    
    if act not in [ 'remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~"
        return jsonify( resp )
    


    member_info = Member.query.filter_by( id = id ).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "指定的会员不存在~"
        return jsonify( resp )

    # 如果存在：
    if act == "remove":
        member_info.status = 0
    elif act == "recover":
        member_info.status = 1
   
    member_info.updated_time = getCurrentDate()
    db.session.add( member_info )
    db.session.commit()
    return jsonify( resp )

