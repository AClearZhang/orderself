# -*- coding:utf-8 -*-
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app
from common.models.food.Food import Food
from common.models.member.MemberCart import MemberCart
from common.models.pay.PayOrder import PayOrder
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.member.MemberAddress import MemberAddress
from common.libs.UrlManager import UrlManager
from common.libs.pay.PayService import PayService
from common.libs.member.CartService import CartService
import json,decimal



@route_api.route( '/order/info', methods=['POST'] )
def orderInfo():
    resp = { 'code': 200, 'msg': "操作成功~", 'data': {} }
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "提交订单失败-2"
        return jsonify( resp )
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads( params_goods )
    
    food_dic = {}
    for item in params_goods_list:
        food_dic[ item['id'] ] = item['number']
    
    food_ids = food_dic.keys()
    food_list = Food.query.filter( Food.id.in_( food_ids ) ).all()
    # 运费先放在这
    yun_price = pay_price = decimal.Decimal( 0.00 )
    data_food_list = []

    if food_list:
        for item in food_list:
            tmp_data = {
                "id": item.id,
                "name": item.name,
                "price": str( item.price ),
                "pic_url": UrlManager.buildImageUrl( item.main_image ),
                "number": food_dic[ item.id ]
            }
            pay_price = pay_price + item.price* int( food_dic[item.id] )
            data_food_list.append( tmp_data )
    total_price = pay_price + yun_price
    
    # 获取地址
    address_info = MemberAddress.query.filter_by( is_default = 1,member_id = member_info.id,status = 1 ).first()
    default_address = ''
    if address_info:
        default_address = {
            "id": address_info.id,
            "name": address_info.nickname,
            "mobile": address_info.mobile,
            "address":"%s%s%s%s"%( address_info.province_str,address_info.city_str,address_info.area_str,address_info.address )
        }
    
    resp['data']['food_list'] = data_food_list
    resp['data']['pay_price'] = str( pay_price )
    resp['data']['yun_price'] = str( yun_price )
    resp['data']['total_price'] = str( total_price )
    resp['data']['default_address'] = default_address
    return jsonify( resp )


@route_api.route( '/order/create', methods=['POST'] )
def orderCreate():
    resp = { 'code': 200, 'msg': '操作成功', 'data': {} }
    req = request.values
    type = req['type'] if 'type' in req else ''
    eat_method = req['eat_method'] if 'eat_method' in req else ''   # 修改eat
    params_goods = req['goods'] if 'goods' in req else None         # json格式字符串
    note = req['note'] if 'note' in req else ''
    express_address_id = int( req['express_address_id'] ) if 'express_address_id' in req and req['express_address_id'] else 0
    # 新增收货地址和备注
    address_info = MemberAddress.query.filter_by( id = express_address_id ).first()
    if not address_info or not address_info.status:
        resp['code'] = -1
        resp['msg'] = "下单失败：快递地址不对~~"
        return jsonify(resp)


    items = []                                                      # json的转化为 列表格式,以供 python内部进行操作
    if params_goods:
        # print( "parms_goods" )
        # app.logger.info( type( params_goods )  )
        items = json.loads( params_goods )                          # 因为传过来的是 str所以进行 json对象话
        # app.logger.info( type( items )  )

        # print( "items: {}".format( type( items ) ) )

    if len( items ) < 1:
        resp['code'] = -1
        resp['msg'] = "下单失败，没有选择商品。"        
        return jsonify( resp )

    # 封装model操作-common/libs/pay/PayService.py
    params = {
        "note":note,
        'express_address_id':address_info.id,
        'express_info':{
            'mobile':address_info.mobile,
            'nickname':address_info.nickname,
            "address":"%s%s%s%s"%( address_info.province_str,address_info.city_str,address_info.area_str,address_info.address )
        }
    }
    member_info = g.member_info
    target = PayService()
    resp = target.createOrder( member_info.id, items, params, eat_method )      # 修改eat

    if resp['code'] == 200 and type == "cart" :
        # 删除cart中的库存
        CartService.delItems( member_info.id, items )

    return jsonify( resp )


'''
暂时未申请到 商家账户——只能先 使用付款的二维码
返回 两张二维码图片；
后台商家上传
'''
@route_api.route( '/order/pay', methods = ['POST'] )
def orderPay():
    resp = { 'code': 200, 'msg': "操作成功~", 'data': {} }
    member_info = g.member_info

    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    pay_order_info = PayOrder.query.filter_by( order_sn = order_sn ).first()
    if not pay_order_info: 
        resp['code'] = -1
        resp['msg'] = "系统繁忙请稍候再试."
        return jsonify( resp )
    
    # 统一下单———获取 openid
    oauth_bind_info = OauthMemberBind.query.filter_by( member_id = member_info.id ).first()
    if not oauth_bind_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙请稍候再试."
        return jsonify( resp )
    
    # 封装微信支付方法
    target_pay = PayService()


    # 需要商家的 付款码！！！ 没有！所以自己  在后台封装——点击审核。   和内容进行分离了进入后台审核操作！
    # 点击一次：
    result = target_pay.orderSuccess( pay_order_id=pay_order_info.id, params= { 'pay_sn': pay_order_info.pay_sn })
    
    # 将微信回调的结果保存在记录表
    # pay_order_callback
    # 在第一次付款成功的时候 回调
    if not result:
        resp['code'] = -1
        resp['msg'] = "系统繁忙请稍候再试."
        return jsonify( resp )
        # target_pay.addPayCallbackData( pay_order_id=pay_order_info.id )
    
    return jsonify( resp )


@route_api.route( "/order/ops", methods=['POST'] )
def orderOps():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~~"
        return jsonify(resp)
    
    target_pay = PayService( )
    if act == "cancel":
        ret = target_pay.closeOrder( pay_order_id=pay_order_info.id )
        if not ret:
            resp['code'] = -1
            resp['msg'] = "系统繁忙。请稍后再试~~"
            return jsonify(resp)
        
    elif act == "confirm":
        ret = target_pay.confirmOrder( pay_order_id=pay_order_info.id ) 
        if not ret:
            resp['code'] = -1
            resp['msg'] = "系统繁忙。请稍后再试~~"
            return jsonify(resp)

    return jsonify(resp)

