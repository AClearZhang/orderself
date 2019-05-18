import sys
sys.path.append(r"C:\Users\acanprince\Desktop\Project\centos_project\order")

# 测试用例书写
from common.libs.user.UserService import UserService



if __name__ == "__main__":

    # 测试筛选数据库 列表
    tmp_food_ids = [ "3", "2", "1", "0", "1" ]
    print(" tmp_food_ids1: {}".format(tmp_food_ids))
    tmp_food_ids = {}.fromkeys(tmp_food_ids).keys()
    print(" tmp_food_ids2: %s"%str(tmp_food_ids))
    food_ids = []
    food_ids = food_ids + list(tmp_food_ids)
    print(" food_ids: {}".format(food_ids))

            

    # print( "login_pwd: {}".format( UserService.genePwd( "123456", "cF3JfH5FJfQ8B2Ba" ) ) )



