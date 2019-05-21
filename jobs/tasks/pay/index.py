# -*- coding: utf-8 -*-
from common.models.pay.PayOrder import  PayOrder
from common.libs.Helper import getFormatDate
from common.libs.pay.PayService import PayService
import datetime
from application import app,db
'''
python manager.py runjob -m pay/index
'''


'''
   下的订单 半个小时之外的：-8的代付款的
   查询出来  将状态职位0
'''

class JobTask():
    def __init__(self):
        pass
    def run(self,params):
        act = params['act'] if 'act' in params else ''

        # 封装多重逻辑-见印象笔记
        if act == "fukuan":
            self.closeFuKuan()
        elif act == "qucan":
            self.closeQuCan()
        elif act == "pinglun":
            self.closePingLun()
        elif not act or act == "all":
            self.closeCheckAll()

        app.logger.info("it's over~~")
        return

    def closeFuKuan( self, params='' ):
        now = datetime.datetime.now()
        inter = app.config['JOB_STATUS_CHANGES']['minutes']
        date_before_30min = now + datetime.timedelta( minutes = int(inter) )
        list = PayOrder.query.filter_by( status = -8 ).\
            filter( PayOrder.created_time <= getFormatDate( date = date_before_30min ) ).all()
        if not list:
            app.logger.info("no data~~")
            return

        pay_target = PayService()
        for item in list:
            pay_target.closeOrder( pay_order_id = item.id )
        app.logger.info("FuKuan is over~~")
        return 
    
    def closeQuCan( self, params='' ):
        now = datetime.datetime.now()
        inter = app.config['JOB_STATUS_CHANGES']['hours']

        date_before_hours = now + datetime.timedelta( hours = int(inter) )
        list = PayOrder.query.filter_by( status = 1, express_status = -6 ).\
            filter( PayOrder.created_time <= getFormatDate( date = date_before_hours ) ).all()
        if not list:
            app.logger.info("no data~~")
            return

        pay_target = PayService()
        for item in list:
            pay_target.confirmOrder( pay_order_id = item.id )
        app.logger.info("QuCan is over~~")
        return 
    
    def closePingLun( self, params='' ):
        now = datetime.datetime.now()
        inter = app.config['JOB_STATUS_CHANGES']['days']

        date_before_days = now + datetime.timedelta( days = int(inter) )
        list = PayOrder.query.filter_by( status = 1,express_status = 1, comment_status = 0 ).\
            filter( PayOrder.created_time <= getFormatDate( date = date_before_days ) ).all()
        if not list:
            app.logger.info("no data~~")
            return

        pay_target = PayService()
        for item in list:
            params = {
                'order_sn': item.order_sn,
                'score': 10,
                'content': "系统默认好评!~",
                'member_id': item.member_id,
            }
        
        ret = pay_target.addComments(params)
        if not ret:
            app.logger.info("error in add pinglun~~")
            return

        app.logger.info("PingLun is over~~")
        return 
    
    def closeCheckAll( self, params='' ):
        self.closeFuKuan()
        self.closeQuCan()
        self.closePingLun()
        app.logger.info("All is over~~")
        return 
    
    