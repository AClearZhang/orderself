from flask import render_template, g
import datetime
'''
自定义分页类
'''
def iPagination( params ):
    import math

    ret = {
        "is_prev":1,
        "is_next":1,
        "from" :0 ,                         # 循环使用
        "end":0,                            # 循环时使用
        "current":0,
        "total_pages":0,
        "page_size" : 0,
        "total" : 0,                        # 总共记录数
        "url":params['url']
    }

    total = int( params['total'] )
    page_size = int( params['page_size'] )
    page = int( params['page'] )
    display = int( params['display'] )
    total_pages = int( math.ceil( total / page_size ) )
    total_pages = total_pages if total_pages > 0 else 1
    if page <= 1:
        ret['is_prev'] = 0

    if page >= total_pages:
        ret['is_next'] = 0

    semi = int( math.ceil( display / 2 ) )

    if page - semi > 0 :
        ret['from'] = page - semi
    else:
        ret['from'] = 1

    if page + semi <= total_pages :
        ret['end'] = page + semi
    else:
        ret['end'] = total_pages

    ret['current'] = page
    ret['total_pages'] = total_pages
    ret['page_size'] = page_size
    ret['total'] = total
    ret['range'] = range( ret['from'],ret['end'] + 1 )
    return ret


'''
统一渲染方法
'''
def ops_render( template, context = {} ):
    if 'current_user' in g:
        context['current_user'] = g.current_user
    
    return render_template( template, **context )


'''
获取当前时间
'''
def getCurrentDate( format = "%Y-%m-%d %H:%M:%S" ):
    return datetime.datetime.now().strftime( format )        # 对当前时间进行格式化

'''
(首先可以 [] 限制查询的范围）根据某个字段获取  一个dic出来

orm  希望查询的字段  希望作为字典的key值  key值对应的已经取出来的id列表
getDictFilterField( FoodCat, FoodCat.id, 'id', [] )

key_field  表示最终希望存储的 key是什么。

[]  限制查询其中的id

返回 map
'''
def getDictFilterField( db_model, select_filed, key_field, id_list ):
    ret = {}
    query = db_model.query
    if id_list and len( id_list ) > 0:
        query = query.filter( select_filed.in_( id_list ) )

    list = query.all()
    if not list:
        return ret
    
    for item in list:
        # id字段不存在
        if not hasattr( item, key_field ):
            break
        # ret[2] = item   ret[3] = item
        ret[ getattr( item, key_field ) ] = item

    return ret

'''
遍历 从指定对象 获取所要 字段的数据
cart_list, 'food_id'   获取全部的food_ids
'''
def selectFilterObj( obj, field ):
    ret = []
    for item in obj:
        if not hasattr( item, field ):
            continue
        if getattr( item, field ) in ret:       # 已经在结果集 不要重复了
            continue
        
        # 添加
        ret.append( getattr( item, field ) )
    
    return ret


'''
    member_comments 里面的 food_ids所有选择出来
    有重复的去重
'''
def selectCommentFoodIDs( obj, field ):
    ret = []
    food_ids = []
    tmp_food_ids = ''
    for item in obj:
        tmp_food_id = []
        if not hasattr( item, field ):
            continue
        if getattr( item, field ) in ret:       # 已经在结果集 不要重复了
            continue
        tmp_str_food_ids = getattr( item, field )
        tmp_food_id += (int(i) for i in tmp_str_food_ids.split('_') if i != '')             # 字符类型的！
        
        # 添加
        ret += tmp_food_id 
        # print( "ret is:{0}".format(ret) )


    # food id有重复——去重
    tmp_food_ids = {}.fromkeys(ret).keys()
    # print( "tmp_food_ids is:{0}".format(tmp_food_ids) )
    food_ids = food_ids + list( tmp_food_ids )
    # print( "food_ids is:{0}".format(food_ids) )
    
    return food_ids


'''
    pay_order_items_map = getDictListFilterField( PayOrderItem,PayOrderItem.pay_order_id,"pay_order_id", pay_order_ids )
    录入： payorder的id
    返回： 对应payorder所有的 item，并且以id为key返回"id":[ {}, {} ]
'''
def getDictListFilterField( db_model,select_filed,key_field,id_list ):
    ret = {}
    query = db_model.query
    if id_list and len( id_list ) > 0:
        query = query.filter( select_filed.in_( id_list ) )

    list = query.all()
    if not list:
        return ret
    for item in list:
        if not hasattr( item,key_field ):
            break
        if getattr( item,key_field ) not in ret:            # 不在结果集，进行 初始化
            ret[getattr(item, key_field)] = []

        ret[ getattr( item,key_field ) ].append(item )      # 每次以id1 进行添加
    return ret


'''
获取格式化的时间
'''
def getFormatDate( date = None ,format = "%Y-%m-%d %H:%M:%S" ):
    if date is None:
        date = datetime.datetime.now()

    return date.strftime( format )
