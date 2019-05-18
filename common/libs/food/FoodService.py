from common.models.food.Food import Food
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.libs.Helper import getCurrentDate
from application import db

class FoodService():

    # 有些时候代码出现了两次，可以进行封装。但是不是所有的 方法都是和进行封装——即 不要为了封装而封装
    @staticmethod
    def setStockChangeLog( food_id = 0,quantity = 0,note = '' ):
        # 差错处理
        if food_id < 1 :
            return False
        # or quantity < 1,不能加，因为 本来库存就是有正有负的 有变化！


        food_info = Food.query.filter_by( id = food_id ).first()
        if not food_id:
            return False

        model_stock_chage = FoodStockChangeLog()
        model_stock_chage.food_id = food_id
        model_stock_chage.unit = quantity                  # 变化改变数量
        model_stock_chage.total_stock = food_info.stock     # 现在的视频库存数量
        model_stock_chage.note = note
        model_stock_chage.created_time = getCurrentDate()
        db.session.add( model_stock_chage )
        db.session.commit()
        return True
    



