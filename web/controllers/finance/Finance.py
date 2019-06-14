# -*- coding: utf-8 -*-
from flask import Blueprint,request,redirect,jsonify
from common.libs.Helper import ops_render
from common.models.member.Member import Member
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from application import  app,db
from common.libs.UrlManager import UrlManager
from common.libs.Helper import iPagination,selectFilterObj,getDictListFilterField,getDictFilterField,getCurrentDate
from common.libs.pay.PayService import PayService
from sqlalchemy import func
import json
route_finance = Blueprint( 'finance_page',__name__ )


'''
    回调财务列表的 首页
'''
@route_finance.route( "/index" )
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1

    query = PayOrder.query

    # 状态值筛选，已支付 已关闭
    if 'status' in req and int( req['status'] ) > -1 :
        query = query.filter( PayOrder.status == int( req['status'] ) )
    # -8待付款 
    if 'status' in req and int( req['status'] ) == -8:
        query = query.filter( PayOrder.status == int( req['status'] ) )
    # -7待审核 -6取餐码
    if 'status' in req and int( req['status'] ) >= -7 and int( req['status'] ) <= -6 :
        query = query.filter( PayOrder.express_status == int( req['status'] ) )

    # 分页
    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }
    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    pay_list = query.order_by(PayOrder.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()
    
    data_list = []
    if pay_list:
        # 获取items map
        pay_order_ids = selectFilterObj( pay_list,"id" )
        pay_order_items_map = getDictListFilterField( PayOrderItem,PayOrderItem.pay_order_id,"pay_order_id", pay_order_ids )

        # 获取food map
        food_mapping = {}
        if pay_order_items_map:
            food_ids = []
            for item in pay_order_items_map:
                #food_ids里面会有重复的，要去重.下面是去重方法：
                tmp_food_ids = selectFilterObj( pay_order_items_map[ item ],"food_id" )
                tmp_food_ids = {}.fromkeys(tmp_food_ids).keys()
                food_ids = food_ids + list( tmp_food_ids )

            
            food_mapping = getDictFilterField( Food,Food.id,"id", food_ids )

        for item in pay_list:
            tmp_data = {
                "id":item.id,
                "status_desc":item.status_desc,
                "order_number":item.order_number,
                "price":item.total_price,
                "pay_time":item.pay_time,
                "created_time":item.created_time.strftime("%Y%m%d%H%M%S")
            }

            # 循环foods进行 取列表{}
            tmp_foods = []
            tmp_order_items = pay_order_items_map[ item.id ]
            for tmp_order_item in tmp_order_items:
                tmp_food_info = food_mapping[ tmp_order_item.food_id ]
                tmp_foods.append( {
                    'name':tmp_food_info.name,
                    'quantity':tmp_order_item.quantity
                } )

            tmp_data['foods'] = tmp_foods
            data_list.append( tmp_data )

    resp_data['list'] = data_list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['pay_status_mapping'] = app.config['PAY_STATUS_MAPPING']
    resp_data['current'] = 'index'

    return ops_render( "finance/index.html",resp_data )


'''
    回调订单的详情页面
'''
@route_finance.route( "/pay-info" )
def info():
    resp_data = {}
    req = request.values
    id = int(req['id']) if 'id' in req else 0

    reback_url = UrlManager.buildUrl("/finance/index")

    # 重定向
    if id < 1:
        return redirect( reback_url )

    pay_order_info = PayOrder.query.filter_by( id = id ).first()
    if not pay_order_info:
        return redirect(reback_url)

    member_info = Member.query.filter_by( id = pay_order_info.member_id ).first()
    if not member_info:
        return redirect(reback_url)

    # 同样通过item 查找，food name。不如新建一个view。
    order_item_list = PayOrderItem.query.filter_by( pay_order_id = pay_order_info.id ).all()
    data_order_item_list = []
    if order_item_list:
        food_map = getDictFilterField(Food, Food.id, "id", selectFilterObj(order_item_list, "food_id"))
        for item in order_item_list:
            tmp_food_info = food_map[ item.food_id ]
            tmp_data = {
                "quantity":item.quantity,
                "price":item.price,
                "name":tmp_food_info.name
            }
            data_order_item_list.append( tmp_data )

    address_info = {}
    if pay_order_info.express_info:
        address_info = json.loads(pay_order_info.express_info)

    resp_data['pay_order_info'] = pay_order_info
    resp_data['pay_order_items'] = data_order_item_list
    resp_data['member_info'] = member_info
    resp_data['address_info'] = address_info
    resp_data['current'] = 'index'
    return ops_render( "finance/pay_info.html",resp_data )

'''
    回调已付款的 财务流水
'''
@route_finance.route( "/account" )
def set():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = PayOrder.query.filter_by( status = 1 )

    # 分页
    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    list = query.order_by(PayOrder.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    # 所有已支付的 流水款.聚合查询.
    # 修改——财务流水 在审核之后才能加入.
    stat_info = db.session.query( PayOrder,func.sum( PayOrder.total_price ).label("total") )\
        .filter( PayOrder.status == 1, PayOrder.express_status != -7 ).first()

    # app.logger.info ( stat_info )
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['total_money'] = stat_info[ 1 ] if stat_info[ 1 ] else 0.00
    resp_data['current'] = 'account'
    return ops_render( "finance/account.html",resp_data )

'''
    处理web回调的 确认收货/审核的信息
'''
@route_finance.route("/ops", methods=[ "POST"])
def orderOps():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    order_id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''

    # pay_order_info = PayOrder.query.filter_by( id = id ).first()
    # if not pay_order_info:
    #     resp['code'] = -1
    #     resp['msg'] = "系统繁忙。请稍后再试~~"
    #     return jsonify(resp)

    app.logger.info("test 1")
    target = PayService()
    
    if act == "take":
        # 确认取餐
        result = target.confirmOrder( pay_order_id=order_id )

    if act == "express":
        # 确认到账——进行sale和成功回调
        # pay_order_info.express_status = -6  # -6
        # pay_order_info.updated_time = getCurrentDate()
        # db.session.add( pay_order_info )

        # 修改新增售卖记录 和 销售量
        result = target.addPayCallbackData( pay_order_id=order_id, type='pay', data='审核确认' )
        app.logger.info("result is1 {}".format( result ))

    if act == "cancel":
        # 取消订单——归还库存
        result = target.addPayCallbackData( pay_order_id=order_id, type='cancel', data='审核取消' )
    if not result:
        app.logger.info("result is 2{}".format( result ))
        
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~~"
        return jsonify(resp)

    return jsonify(resp)
