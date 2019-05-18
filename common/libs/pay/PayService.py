from application import db, app
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrderCallbackData import PayOrderCallbackData   # 支付成功与失败
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
from common.libs.Helper import getCurrentDate
from common.libs.food.FoodService import FoodService

import decimal
import time
import hashlib
import random
import datetime
import json
from sqlalchemy import func


class PayService():
    def __init__(self):
        pass
    '''
        创建订单
    '''

    def createOrder(self, member_id, items=None, params=None, eat_method=''):
        resp = {'code': 200, 'msg': '操作成功', 'data': {}}

        pay_price = decimal.Decimal(0.00)

        continue_cnt = 0
        food_ids = []
        for item in items:
            if decimal.Decimal(item['price']) < 0:
                continue_cnt += 1
                continue
            pay_price = pay_price + \
                (decimal.Decimal(item['price']) * int(item['number']))
            food_ids.append(item['id'])

        if continue_cnt >= len(items):   # 下单数量超过  选中数量，不成立
            resp['code'] = -1
            resp['msg'] = "商品items为空"
            return resp

        yun_price = params['yun_price'] if params and 'yun_price' in params else 0
        note = params['note'] if params and 'note' in params else ''
        express_address_id = params['express_address_id'] if params and 'express_address_id' in params else 0
        express_info = params['express_info'] if params and 'express_info' in params else {}

        yun_price = decimal.Decimal(yun_price)
        total_price = pay_price + yun_price
        # 并发处理，加入库存
        # 悲观锁  或者  乐观锁
        try:
            #   db.session.query( Food ).filter( Food.id.in_( food_ids ) )\

            tmp_food_list = db.session.query(Food).filter(Food.id.in_(food_ids))\
                .with_for_update().all()                                                # 进行悲观锁 操作 # z只有rollback或者commit都能解锁;
            # time.sleep( 10 )
            # 下单表 和 下单从表--加入数据
            tmp_food_stock_mapping = {}
            for tmp_item in tmp_food_list:
                # 注意对象不能用数组来做，只能用属性值！
                tmp_food_stock_mapping[tmp_item.id] = tmp_item.stock

            model_pay_order = PayOrder()
            model_pay_order.order_sn = self.geneOrderSn()                           # 产生的 随机订单号
            model_pay_order.member_id = member_id
            model_pay_order.total_price = total_price
            model_pay_order.pay_price = pay_price
            model_pay_order.yun_price = yun_price
            model_pay_order.note = note
            model_pay_order.status = -8
            model_pay_order.express_status = -8
            model_pay_order.express_address_id = express_address_id
            model_pay_order.express_info = json.dumps( express_info )
            model_pay_order.prepay_id = eat_method                                  # 修改eat
            model_pay_order.updated_time = getCurrentDate()
            db.session.add(model_pay_order)

            # 从表添加
            for item in items:
                tmp_left_stock = tmp_food_stock_mapping[item['id']]

                # 异常判断/处理
                if decimal.Decimal(item['price']) < 0:
                    continue
                if int(item['number']) > int(tmp_left_stock):
                    # 直接抛出异常
                    raise Exception("您购买的美食太火爆了，剩余：%s,您购买：%s" %
                                    (tmp_left_stock, item['number']))

                # 数据库处理
                tmp_ret = Food.query.filter_by(id=item['id']).update({
                    "stock": int(tmp_left_stock) - int(item['number'])
                })

                if not tmp_ret:
                    raise Exception("下单失败请重新下单")

                tmp_pay_item = PayOrderItem()
                tmp_pay_item.pay_order_id = model_pay_order.id
                tmp_pay_item.member_id = member_id
                tmp_pay_item.quantity = item['number']
                tmp_pay_item.price = item['price']
                tmp_pay_item.food_id = item['id']
                tmp_pay_item.note = note
                tmp_pay_item.updated_time = tmp_pay_item.created_time = getCurrentDate()
                db.session.add(tmp_pay_item)
                # 库存处理，减少库存
                FoodService.setStockChangeLog(
                    item['id'],  -item['number'], "在线购买")

            db.session.commit()
            # 下单成功，返回相应数据
            resp['data'] = {
                'id': model_pay_order.id,
                'order_sn': model_pay_order.order_sn,
                'total_price': str(total_price),
            }

        except Exception as e:
            # 如果抛出错误，进行回滚
            db.session.rollback()
            print(e)
            resp['code'] = -1
            resp['msg'] = "下单失败请重新下单"
            resp['msg'] = str(e)
            return resp

        return resp

    # 和上方的方法 配合使用
    def geneOrderSn(self):
        m = hashlib.md5()   # 实例化
        sn = None
        while True:
            # 生成自己的随机字段，进行md5加密
            str = "%s-%s" % (int(round(time.time()*1000)),
                             random.randint(0, 9999999))
            m.update(str.encode("utf-8"))
            sn = m.hexdigest()
            # 查询数据库中是否 存在，存在则舍弃 重新获取
            if not PayOrder.query.filter_by(order_sn=sn).first():
                break

        return sn

    '''
        取消订单
    '''

    def closeOrder(self, pay_order_id=0):
        if pay_order_id < 1:
            return False
        pay_order_info = PayOrder.query.filter_by(
            id=pay_order_id, status=-8).first()
        if not pay_order_info:
            return False

        pay_order_items = PayOrderItem.query.filter_by(
            pay_order_id=pay_order_id).all()
        if pay_order_items:
            # 需要归还库存
            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                if tmp_food_info:
                    tmp_food_info.stock = tmp_food_info.stock + item.quantity
                    tmp_food_info.updated_time = getCurrentDate()
                    db.session.add(tmp_food_info)
                    db.session.commit()
                    FoodService.setStockChangeLog(
                        item.food_id, item.quantity, "订单取消")

        pay_order_info.status = 0
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return True

    '''
        平时不要写 非常特定的方法！太局限，不具有 普适性。
        马上付款，付款成功之后的方法调用
        将 pay_order  状态status1  待审核express_status -7
    '''

    def orderSuccess(self, pay_order_id=0, params=None):
        try:
            pay_order_info = PayOrder.query.filter_by(id=pay_order_id).first()
            # 不存在 或者 不是未支付或者待审核——就不需要我们处理了。 说明 已经处理过了。
            if not pay_order_info or pay_order_info.status not in [-8, -7]:
                return True

            # pay_order_info.pay_sn = params['pay_sn'] if params and 'pay_sn' in params else ''       # pay_sn 支付第三方流水账号信息。不需要了。
            # 改为计数且为字符类型

            # 第一次
            if params and 'pay_sn' in params:
                if params['pay_sn'] == '':
                    pay_order_info.pay_sn = "1"

                    # 售卖变更记录： FoodSaleChangeLog
                    pay_order_items = PayOrderItem.query.filter_by(
                        pay_order_id=pay_order_id).all()
                    for order_item in pay_order_items:
                        tmp_model_sale_log = FoodSaleChangeLog()
                        tmp_model_sale_log.food_id = order_item.food_id
                        tmp_model_sale_log.quantity = order_item.quantity
                        tmp_model_sale_log.price = order_item.price
                        tmp_model_sale_log.member_id = order_item.member_id
                        tmp_model_sale_log.created_time = getCurrentDate()
                        db.session.add(tmp_model_sale_log)

                else:
                    num = int(params['pay_sn'])
                    app.logger.info("The touch num is:{0}".format(num+1))
                    pay_order_info.pay_sn = str(num+1)
                    return False
            else:
                pay_order_info.pay_sn = ''
            # end第一次

            # 改变发货状态
            # pay_order_info.pay_sn = params['pay_sn'] if params and 'pay_sn' in params else ''
            pay_order_info.status = 1
            # 设置为待发货/待审核
            pay_order_info.express_status = -7
            pay_order_info.pay_time = getCurrentDate()
            pay_order_info.updated_time = getCurrentDate()
            db.session.add(pay_order_info)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(e)
            return False

        # 加入通知队列，做消息提醒和
        # QueueService.addQueue( "pay",{
        #     "member_id": pay_order_info.member_id,
        #     "pay_order_id":pay_order_info.id
        # })
        return True

    # 包括我们的`pay_data` text NOT NULL COMMENT '支付回调信息',
    #          `refund_data` text NOT NULL COMMENT '退款回调信息',
    #           type：表明是 付款？审核？还是退款？
    def addPayCallbackData(self, pay_order_id=0, type='pay', data=''):
        model_callback = PayOrderCallbackData()
        model_callback.pay_order_id = pay_order_id
        if type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        # db.session.commit()

        # 每个月的月底进行统计或者更新
        # 更新销售总量
        pay_order_items = PayOrderItem.query.filter_by( pay_order_id=pay_order_id).all()
        notice_content = []
        if pay_order_items:
            date_from = datetime.datetime.now().strftime("%Y-%m-01 00:00:00")
            date_to = datetime.datetime.now().strftime("%Y-%m-31 23:59:59")
            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                if not tmp_food_info:
                    continue

                notice_content.append("%s %s份" % (tmp_food_info.name, item.quantity))

                # 当月数量
                # query( 0, 1) 当中指针为0 和 1的两个对象。
                tmp_stat_info = db.session.query(FoodSaleChangeLog, func.sum(FoodSaleChangeLog.quantity).label("total")) \
                    .filter(FoodSaleChangeLog.food_id == item.food_id)\
                    .filter(FoodSaleChangeLog.created_time >= date_from, FoodSaleChangeLog.created_time <= date_to).first()

                app.logger.info("当月数量：tmp_stat_info:{0}".format(tmp_stat_info) )
                tmp_month_count = tmp_stat_info[1] if tmp_stat_info[1] else 0
                tmp_food_info.total_count += 1
                tmp_food_info.month_count = tmp_month_count
                db.session.add(tmp_food_info)
                
            # 统计end
        db.session.commit()
        return True
