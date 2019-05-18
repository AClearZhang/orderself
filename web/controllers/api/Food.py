# -*- coding: utf-8 -*-
'''
小程序 api首页接口
# 接口一：
# 滑动栏  菜品分类  

# 接口二：
# 菜品详情
'''
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app, db
import requests, json
from common.libs.Helper import getCurrentDate, iPagination, getDictFilterField, selectFilterObj
from common.models.food.Food import Food
from common.models.food.FoodCat import FoodCat
from common.libs.UrlManager import UrlManager
from sqlalchemy import or_
from common.models.member.MemberCart import MemberCart
from common.models.member.MemberComments import MemberComments
from common.models.member.Member import Member

shop_cat_id = int(app.config['SHOP_USING']['cat_id'])

@route_api.route("/food/index")
def foodIndex():
    resp = { 'code':200, 'msg': '操作成功', 'data':{} }
    # 取出所有的分类信息
    # 修改catid
    cat_list = FoodCat.query.filter( FoodCat.status == 1, FoodCat.id != shop_cat_id).order_by( FoodCat.weight.desc() ).all()
    # 构造出全部类别的数组，将一个个的字典放置进去：方便进行前端 类别的展示
    all_cat_list = []
    all_cat_list.append({
        'id': 0,
        'name': '推荐'
    })
    '''
    返回 id name
    '''
    if cat_list:
        for item in cat_list:
            tmp_data = {
                "id": item.id,
                "name": item.name
            }
            all_cat_list.append( tmp_data )
    resp['data']['cat_list'] = all_cat_list

    # 修改catid banner
    '''
    取出比较火的菜品，进行前端banner图展示
    销售量最大  的没事列表
    返回：id pic_url
    '''
    food_list = Food.query.filter_by( status = 1 )\
                .order_by( Food.total_count.desc(),Food.cat_id.desc() ).limit(3).all()
    all_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                "id": item.id,
                "pic_url": UrlManager.buildImageUrl( item.main_image )
            }
            all_food_list.append( tmp_data )

    resp['data']['banner_list'] = all_food_list
    return jsonify( resp )


'''
search 查询 和 列表刷新展示
api 本就是请求+返回数据
'''
@route_api.route("/food/search")
def foodSearch():
    # 分页搜索与简单搜索
    resp = { 'code':200, 'msg': '操作成功', 'data':{} }
    req = request.values
    '''
    注意是要在 对应的分类里面进行复合查询
    '''
    cat_id = int( req['cat_id'] ) if 'cat_id' in req else 0
    mix_kw = str( req['mix_kw'] ) if 'mix_kw' in req else ''
    p = int( req['p'] ) if 'p' in req else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = ( p - 1 )*page_size

    # 修改catid
    query = Food.query.filter( Food.status == 1, Food.cat_id != shop_cat_id )
    if 'cat_id' in req and int( req['cat_id'] ) > 0 :
        query = query.filter( Food.cat_id == int( req['cat_id'] ) )
    if mix_kw:
        rule = or_(Food.name.ilike("%{0}%".format(mix_kw)), Food.tags.ilike("%{0}%".format(mix_kw)))
        query = query.filter( rule )

    food_list = query.order_by( Food.total_count.desc(), Food.id.desc()).offset( offset ).limit(page_size).all()

    # # 修改
    # # 初始化购物车的数量
    # member_info = g.member_info
    # if not member_info:
    #     resp['code'] = -1
    #     resp['msg'] = "获取失败，未登录~"
    #     return jsonify( resp )
    # cart_list = MemberCart.query.filter_by( member_id = member_info.id ).all()
    # cart_foods_id = selectFilterObj( cart_list, 'food_id' )
    # cart_map = getDictFilterField( MemberCart, None, 'food_id', [])

     
    # 转化为前端需要的list结构
    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str( item.price ),                    # 出问题了为什么？因为json 传出去decimal！
                'min_price': str( item.price ),
                'sales': item.total_count,
                'pic_url': UrlManager.buildImageUrl( item.main_image )
            }
            data_food_list.append( tmp_data )

    resp['data']['list'] = data_food_list
    # 判断是否还需要发送数据
    resp['data']['has_more'] = 0 if len( data_food_list ) < page_size else 1

    return jsonify( resp )

'''
    返回food 和 类别
'''
@route_api.route( '/food/menu/list' )
def menuList():
    # 分页搜索与简单搜索
    resp = { 'code':200, 'msg': '操作成功', 'data':{} }
    req = request.values

    # 添加分页处理
    p = int( req['p'] ) if 'p' in req else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = ( p - 1 )*page_size

    '''
    注意是要在 对应的分类里面进行复合查询
    '''
    cat_id = int( req['cat_id'] ) if 'cat_id' in req else 0
    # 修改cat
    query = Food.query.filter( Food.status == 1, Food.cat_id != shop_cat_id )
    if 'cat_id' in req and int( req['cat_id'] ) > 0 :
        query = query.filter( Food.cat_id == int( req['cat_id'] ) )
    # 查找food
    food_list = query.order_by( Food.total_count.desc(), Food.id.desc()).offset(offset).limit(page_size).all()

    # 返回类别 # 修改cat
    cat_list = FoodCat.query.filter( FoodCat.status == 1, FoodCat.id != shop_cat_id ).order_by( FoodCat.weight.desc() ).all()
    # 构造出全部类别的数组，将一个个的字典放置进去：方便进行前端 类别的展示
    all_cat_list = []
    all_cat_list.append({
        'id': 0,
        'name': '全部'
    })
    '''
    返回 id name
    '''
    if cat_list:
        for item in cat_list:
            tmp_data = {
                "id": item.id,
                "name": item.name
            }
            all_cat_list.append( tmp_data )
    resp['data']['cat_list'] = all_cat_list

    

    # 修改
    # 初始化购物车的数量
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "获取失败，未登录~"
        return jsonify( resp )
    cart_list = MemberCart.query.filter_by( member_id = member_info.id ).all()
    cart_foods_id = selectFilterObj( cart_list, 'food_id' )
    cart_map = getDictFilterField( MemberCart, None, 'food_id', [])

     
    # 转化为前端需要的list结构
    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str( item.price ),                    # 出问题了为什么？因为json 传出去decimal！
                'min_price': str( item.price ),
                'sales': item.total_count,
                'quantity': cart_map[item.id].quantity if item.id in cart_foods_id else 0,                                  # 选中几个
                'pic_url': UrlManager.buildImageUrl( item.main_image )
            }
            data_food_list.append( tmp_data )

    resp['data']['list'] = data_food_list
    # print( "P is:{0}  Len is:{1}".format( p, len( data_food_list )  ) )
    resp['data']['has_more'] = 0 if len( data_food_list ) < page_size else 1        # 0表示后面没有了,1表示后面还有
    return jsonify( resp )


@route_api.route( "/food/info" )
def foodInfo():
    resp = { 'code':200, 'msg': '操作成功', 'data':{} }
    req = request.values
    id = int( req['id'] ) if 'id' in req else 0
    food_info = Food.query.filter_by( id = id ).first()
    # 注意：不存在 或者 美食已被删除
    if not food_info or not food_info.status:
        resp['code'] = -1
        resp['msg'] = "美食已下架"
        return jsonify( resp )

    # 购物车右上角角标
    member_info = g.member_info
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by( member_id=member_info.id ).count()



    resp['data']['info'] = {
        'id': id,
        'name': food_info.name,
        'summary': food_info.summary,
        'total_count': food_info.total_count,
        'comment_count': food_info.comment_count,
        'main_image': UrlManager.buildImageUrl( food_info.main_image ),
        'price': str( food_info.price ),
        'stock': food_info.stock,
        'pics': [  UrlManager.buildImageUrl( food_info.main_image ) ]
    }
    resp['data']['cart_number'] = cart_number
    return jsonify( resp )

@route_api.route( '/food/comments' )
def foodComments():
    resp = { 'code': 200, 'msg': '操作成功~', 'data': {} }
    req = request.values
    id = int( req['id'] ) if 'id' in req else 0
    
    # 使用 ilike查询; 且注意这里只查询出来了五条
    query = MemberComments.query.filter( MemberComments.food_ids.ilike( "%_{0}_%".format(id) ) )
    list = query.order_by( MemberComments.id.desc() ).limit( 5 ).all()
    data_list = []
    if list:
        member_map = getDictFilterField( Member, Member.id, 'id', selectFilterObj( list, "member_id" ) )
        for item in list:
            if item.member_id not in member_map:
                continue
            tmp_member_info = member_map[ item.member_id ]
            tmp_data = {
                "score": item.score_desc,
                "date": item.created_time.strftime( "%Y-%m-%d %H:%M:%S" ),
                "content": item.content,
                "user": {
                    "nickname": tmp_member_info.nickname,
                    "avatar_url": tmp_member_info.avatar,
                }
            }
            data_list.append( tmp_data )
    
    resp['data']['list'] = data_list
    resp['data']['count'] = query.count()
    return jsonify( resp )

