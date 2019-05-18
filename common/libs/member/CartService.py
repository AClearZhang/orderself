# 用户逻辑操作包！
import hashlib, requests, random, string, json
from application import app, db
from common.models.member.MemberCart import MemberCart
from common.libs.Helper import getCurrentDate

class CartService():

    '''
    设置加入购物车-单项
    '''
    @staticmethod
    def setItems( member_id=0, food_id=0 ,number=0 ):
        if member_id < 1 or food_id < 1 or number < 1:
            return False
        # 判断是否存在：存在则编辑/重置/不进行添加操作   不存在则添加
        cart_info = MemberCart.query.filter_by( food_id=food_id, member_id=member_id ).first()
        if cart_info:
            model_cart = cart_info
        else:# 添加
            model_cart = MemberCart()
            model_cart.member_id = member_id
            model_cart.created_time = getCurrentDate()
        
        model_cart.food_id = food_id
        model_cart.quantity = number
        model_cart.updated_time = getCurrentDate()
        db.session.add( model_cart )
        db.session.commit()
        return True
    '''
    设置删除购物车数据
    '''
    @staticmethod
    def delItems( member_id=0, items = None ):
        if member_id < 1 or not items:
            return False
        
        for item in items:
            MemberCart.query.filter_by( food_id = item['id'], member_id = member_id ).delete()

        db.session.commit()
        return True
