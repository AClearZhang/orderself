# -*- coding:utf-8 -*-
from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.food.Food import Food
from common.models.member.MemberCart import MemberCart
from common.libs.member.CartService import CartService
from common.libs.UrlManager import UrlManager
from common.libs.Helper import selectFilterObj, getDictFilterField
import json


@route_api.route( '/cart/index' )
def cartIndex():
    resp = { 'code': 200,'msg': '操作成功~','data': {} }
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "获取失败，未登录~"
        return jsonify( resp )

    # 取出购物车list
    cart_list = MemberCart.query.filter_by( member_id = member_info.id ).all()
    data_cart_list = []
    # 业务封装
    if cart_list:                                                   # 重点逻辑！
        food_ids = selectFilterObj( cart_list, 'food_id' )          # 获取所有的 food_id
        food_map = getDictFilterField( Food, Food.id, 'id', food_ids )

        for item in cart_list:
            tmp_food_info = food_map[ item.food_id ]
            tmp_data = {
                'id': item.id,
                'food_id': item.food_id,
                'number': item.quantity,
                'name': tmp_food_info.name,
                'price': str(tmp_food_info.price),
                'pic_url': UrlManager.buildImageUrl( tmp_food_info.main_image ),
                'active': True                                                      #  默认是否为选中状态
            }
            data_cart_list.append( tmp_data )
    resp['data']['list'] = data_cart_list
    return jsonify( resp )



@route_api.route('/cart/set', methods=['POST'])
def setCart():
    resp = { 'code': 200,'msg': '操作成功~','data': {} }
    req = request.values

    food_id = int( req['id'] ) if 'id' in req else 0
    number = int( req['number'] ) if 'number' in req else 0
    if food_id < 1 or number < 1:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-1"
        return jsonify( resp )

    # 是否存在用户！
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-2"
        return jsonify( resp )

    # 判断food是否可以收藏
    food_info = Food.query.filter_by( id = food_id ).first()
    if not food_info:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-3"
        return jsonify( resp )
    if food_info.stock < number:
        resp['code'] = -1
        resp['msg'] = "添加失败-库存不足.请重新添加."
        return jsonify( resp )
    
    
    ret = CartService.setItems( member_id=member_info.id, food_id=food_info.id, number=number ) # 统一封装 数据库操作model 部分函数
    if not ret:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-4"
        return jsonify( resp )
    
    return jsonify( resp )


@route_api.route( "/cart/del", methods=['POST'] )
def delCart():
    resp = { 'code': 200,'msg': '操作成功~','data': {} }
    req = request.values

    params_goods = req['goods'] if 'goods' in req else None
    
    items = []
    if params_goods:
        items = json.loads(params_goods)
    
    # 差错处理
    if not items or len( items ) < 1:
        return jsonify( resp )


    # 删除操作
    # 是否存在用户！
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "删除购物车失败-1"
        return jsonify( resp )
    
    ret = CartService.delItems( member_id=member_info.id, items=items)
    if not ret:
        resp['code'] = -1
        resp['msg'] = '删除购物车失败-2'
        return jsonify( resp )
    

    return jsonify( resp )

