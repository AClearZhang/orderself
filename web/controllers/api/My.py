# -*- coding:utf-8 -*-
from web.controllers.api import route_api
from application import app, db
from flask import request, jsonify, g
from common.libs.UrlManager import UrlManager
from common.libs.Helper import selectFilterObj, getDictFilterField, getCurrentDate
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.member.MemberComments import MemberComments
import json, datetime

'''
    返回要支付的二维码信息
'''
@route_api.route( '/my/order/payimage' )
def payImage():
    resp = {'code': 200, 'msg': "查找成功", 'data': {}}
    member_info = g.member_info
    tmp_food_pay_image = Food.query.filter_by( tags="二维码" ).all()

    if not  tmp_food_pay_image:
        resp['code'] = -1
        resp['msg'] = "查找失败"
        return jsonify( resp )
    
    main_pic = []
    for item in tmp_food_pay_image:
        tmp_image = item.main_image
        if not tmp_image:
            continue

        tmp_image = UrlManager.buildImageUrl( tmp_image )
        main_pic.append( tmp_image )

    resp['data']['main_pic'] = main_pic
    return jsonify( resp )


'''
    V2.0  第一版本的回调数据错误！
    查询并返回所有 订单的列表。
    data: status  带过来的是当前状态——
    返回： status express_status comment_status   进行区分
    
    statusType: ["待付款", "待审核", "待收货", "待评价", "已完成","已关闭"],
    status:[ "-8","-7","-6","-5","1","0" ],
'''
@route_api.route( '/my/order', methods=['POST'] )
def myOrder():
    resp = {'code': 200, 'msg': "订单成功", 'data': {}}
    member_info = g.member_info
    req = request.values

    status = int( req['status'] ) if 'status' in req else 0
    # 取出payorder表进行 展示
    query = PayOrder.query.filter_by( member_id = member_info.id )
    if status == -8:  # 等待付款
        query = query.filter( PayOrder.status == -8 )
    elif status == -7: # 待发货
        query = query.filter( PayOrder.status == 1, PayOrder.express_status == -7, PayOrder.comment_status == 0 )
    elif status == -6: # 待确认
        query = query.filter( PayOrder.status == 1, PayOrder.express_status == -6, PayOrder.comment_status == 0 )
    elif status == -5: # 待评价
        query = query.filter( PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 0 )  # 修改
    elif status == 1: # 已完成
        query = query.filter( PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 1 )
    else:# 已关闭
        query = query.filter( PayOrder.status == 0 )

    pay_order_list = query.order_by( PayOrder.id.desc() ).all()
    # 取出所有结果  进行格式化,并返回数据
    data_pay_order_list = []
    '''
    返回： 下单时间、订单号、备注、合计金额 —— 都在PayOrderItem,member_id payorder_id 
           高能信息 复杂筛选机制
           前方高能 预警！！！！！！
    '''

    if pay_order_list:
        pay_order_ids = selectFilterObj( pay_order_list, 'id' )
        # 一个信息
        pay_order_item_list = PayOrderItem.query.filter( PayOrderItem.pay_order_id.in_( pay_order_ids ) ).all()  # 不需要了：member_id== member_info.id,
        # 对应取出 food的相关信息,得到对应的图片
        food_ids = selectFilterObj( pay_order_item_list, 'food_id' )
        food_map = getDictFilterField( Food, Food.id, 'id', food_ids )

        '''
            {
                    status: -8,
                    status_desc: "待支付",
                    date: "2018-07-01 22:30:23",
                    order_number: "20180701223023001",
                    note: "记得周六发货",
                    total_price: "85.00",
                    goods_list: [
                        {
                            pic_url: "/images/food.jpg"
                        },
                        {
                            pic_url: "/images/food.jpg"
                        }
                    ]
            }
        '''
        # 遍历获取出来，并组装数据给 data_pay_order_list
        # 拿出所有的order——一对多个 item

        # 没有视图——不通过 数据库加压的复杂查询————只能通过python后端进行复杂查询
        # 复杂查询当中，如果有多个for 循环： 应该进行map 变量的设计。

        pay_order_item_map = {}
        if pay_order_item_list:
            for item in pay_order_item_list:
                # 进行初始化
                if item.pay_order_id not in pay_order_item_map:
                    pay_order_item_map[ item.pay_order_id ] = []

                tmp_food_info = food_map[ item.food_id  ]
                pay_order_item_map[ item.pay_order_id ].append({
                    "id": item.id,
                    "food_id": item.food_id,
                    "quantity": item.quantity,
                    "pic_url": UrlManager.buildImageUrl( tmp_food_info.main_image ),
                    "name": tmp_food_info.name
                })
        # 添加至主表
        for item in pay_order_list:
            tmp_data = {
                "status": item.pay_status,
                "status_desc":  item.status_desc,# 状态描述
                "date": item.created_time.strftime( "%Y-%m-%d %H:%M:%S" ),
                "order_number": item.order_number,
                "take_number": str(item.id).zfill(5),
                "order_sn": item.order_sn,
                "note": item.note,
                "total_price": str( item.total_price ),
                "goods_list": pay_order_item_map[ item.id ], # 在内部判断，循环 麻烦。所以有了 pay_order_item_map
            }
            data_pay_order_list.append( tmp_data )
    
    resp['data']['order_list'] = data_pay_order_list
    return jsonify( resp )


'''
    用户查看订单详情  返回首页
    返回 付款二维码
'''
@route_api.route("/my/order/info")
def myOrderInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    pay_order_info = PayOrder.query.filter_by( member_id=member_info.id ,order_sn = order_sn).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    # 收货地址
    express_info = {}
    if pay_order_info.express_info:
        express_info = json.loads( pay_order_info.express_info )

    tmp_deadline = pay_order_info.created_time + datetime.timedelta(minutes=30)
    info = {
        "order_sn":pay_order_info.order_sn,
        "status":pay_order_info.pay_status,
        "status_desc":pay_order_info.status_desc,
        "pay_price":str( pay_order_info.pay_price),
        "yun_price":str( pay_order_info.yun_price),
        "total_price":str( pay_order_info.total_price),
        "address":express_info,
        "goods": [],
        "deadline":tmp_deadline.strftime("%Y-%m-%d %H:%M")
    }

    pay_order_items = PayOrderItem.query.filter_by( pay_order_id = pay_order_info.id  ).all()
    if pay_order_items:
        food_ids = selectFilterObj( pay_order_items , "food_id")
        # 未修改外键查询
        food_map = getDictFilterField(Food, Food.id, "id", food_ids)
        for item in pay_order_items:
            tmp_food_info = food_map[item.food_id]
            tmp_data = {
                "name": tmp_food_info.name,
                "price": str( item.price ),
                "unit": item.quantity,
                "pic_url": UrlManager.buildImageUrl( tmp_food_info.main_image ),
            }
            info['goods'].append( tmp_data )
    resp['data']['info'] = info
    return jsonify(resp)



@route_api.route( '/my/comment/list' )
def myCommentList():
    resp = { 'code': 200, 'msg': "操作成功~", 'data': {} }
    member_info = g.member_info
    comment_list = MemberComments.query.filter_by( member_id=member_info.id )\
        .order_by(MemberComments.id.desc()).all()
    data_comment_list = []
    if comment_list:
        pay_order_ids = selectFilterObj( comment_list,"pay_order_id" )
        pay_order_map = getDictFilterField( PayOrder,PayOrder.id,"id",pay_order_ids )
        for item in comment_list:
            tmp_pay_order_info = pay_order_map[ item.pay_order_id ]
            tmp_data = {
                "date":item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content":item.content,
                "order_number":tmp_pay_order_info.order_number
            }
            data_comment_list.append( tmp_data )
    resp['data']['list'] = data_comment_list
    return jsonify( resp )
   
@route_api.route("/my/comment/add",methods = [ "POST" ])
def myCommentAdd():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    score = req['score'] if 'score' in req else 10
    content = req['content'] if 'content' in req else ''

    pay_order_info = PayOrder.query.filter_by( member_id=member_info.id ,order_sn = order_sn).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    if pay_order_info.comment_status:
        resp['code'] = -1
        resp['msg'] = "已经评价过了~~"
        return jsonify(resp)

    pay_order_items = PayOrderItem.query.filter_by( pay_order_id = pay_order_info.id ).all()
    food_ids = selectFilterObj( pay_order_items,"food_id" )
    tmp_food_ids_str = '_'.join(str(s) for s in food_ids if s not in [None])
    model_comment = MemberComments()
    model_comment.food_ids = "_%s_"%tmp_food_ids_str
    model_comment.member_id = member_info.id
    model_comment.pay_order_id = pay_order_info.id
    model_comment.score = score
    model_comment.content = content
    db.session.add( model_comment )

    pay_order_info.comment_status = 1
    pay_order_info.updated_time = getCurrentDate()
    db.session.add( pay_order_info )

    db.session.commit()
    return jsonify(resp)


