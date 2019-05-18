# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, redirect
from common.libs.Helper import ops_render, getCurrentDate, iPagination, getDictFilterField
from common.libs.UrlManager import UrlManager
from common.libs.food.FoodService import FoodService
from common.models.food.FoodCat import FoodCat
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.models.food.Food import Food
from application import app, db
from decimal import Decimal
from sqlalchemy import or_

route_food = Blueprint( 'food_page',__name__ )

@route_food.route( "/index" )
def index():
    resp_data = {}
    req = request.values

    # 分页 + 复杂的符合搜索逻辑.
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = Food.query
    if 'mix_kw' in req:
        rule = or_(Food.name.ilike("%{0}%".format(req['mix_kw'])), Food.tags.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter( rule )

    if 'status' in req and int( req['status'] ) > -1 :
        query = query.filter( Food.status == int( req['status'] ) )

    if 'cat_id' in req and int( req['cat_id'] ) > 0 :
        query = query.filter( Food.cat_id == int( req['cat_id'] ) )

    page_params = {
        'total':query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page':page,
        'display':app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page),"")
    }

    pages = iPagination( page_params )
    offset = ( page - 1 ) * app.config['PAGE_SIZE']
    list = query.order_by( Food.id.desc() ).offset( offset ).limit( app.config['PAGE_SIZE'] ).all()

    cat_mapping = getDictFilterField( FoodCat,FoodCat.id,"id",[] )                                      # 为了获取cat所有分类的字典，构造一个获取的字典函数。
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['cat_mapping'] = cat_mapping
    resp_data['current'] = 'index'
    return ops_render( "food/index.html",resp_data )

'''
菜品详情展示 + 库存变更展示
'''

@route_food.route( "/info" )
def info():
    resp_data = {}
    req = request.args
    id = int(req.get("id", 0))
    reback_url = UrlManager.buildUrl("/food/index")

    if id < 1:
        return redirect( reback_url )

    info = Food.query.filter_by( id =id ).first()
    if not info:
        return redirect( reback_url )

    stock_change_list = FoodStockChangeLog.query.filter( FoodStockChangeLog.food_id == id )\
        .order_by( FoodStockChangeLog.id.desc() ).all()

    resp_data['info'] = info
    resp_data['stock_change_list'] = stock_change_list
    resp_data['current'] = 'index'                          # 因为有切换的页面——  index / 
    return ops_render( "food/info.html",resp_data )


@route_food.route( "/set", methods=['GET', 'POST'] )
def set():
    if request.method == "GET":
        resp_data = {}
        cat_list = FoodCat.query.all()
        resp_data['cat_list'] = cat_list
        resp_data['current'] = 'index'

        #  取出food id进行set页面的渲染
        req = request.args
        id = int( req.get( 'id', 0) )
        info = Food.query.filter_by( id = id ).first()
        if info and info.status != 1:
            return redirect( UrlManager.buildUrl("/food/index") )

        resp_data['info'] = info
        return ops_render( "food/set.html", resp_data ) 

    resp={ 'code': 200, 'msg': '操作成功~', 'data':{} }
    req = request.values
    
    id = int(req['id']) if 'id' in req and req['id'] else 0                               # 上来是空值所以报错 解决用and
    cat_id = int( req['cat_id'] ) if 'cat_id' in req else 0
    name = req['name'] if 'name' in req else ''
    price = req['price'] if 'price' in req else ''
    main_image = req['main_image'] if 'main_image' in req else ''
    summary = req['summary'] if 'summary' in req else ''     
    stock = int(req['stock']) if 'stock' in req else ''     
    tags = req['tags'] if 'tags' in req else ''

    if cat_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择分类"
        return jsonify( resp )

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的名称~~"
        return jsonify(resp)

    if not price or len( price ) < 1.00:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(resp)

    price = Decimal(price).quantize(Decimal('0.00'))                                 # 100.00 价格都是保留两位数字的
    if  price <= 0:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(resp)

    if main_image is None or len(main_image) < 3:
        resp['code'] = -1
        resp['msg'] = "请上传封面图~~"
        return jsonify(resp)

    if summary is None or len(summary) < 10:
        resp['code'] = -1
        resp['msg'] = "请输入图书描述，并不能少于10个字符~~"
        return jsonify(resp)

    if stock < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的库存量~~"
        return jsonify(resp)

    if tags is None or len(tags) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入标签，便于搜索~~"
        return jsonify(resp)

    food_info = Food.query.filter_by(id=id).first()
    before_stock = 0
    if food_info:
        model_food = food_info
        before_stock = model_food.stock
    else:
        model_food = Food()
        model_food.status = 1
        model_food.created_time = getCurrentDate()

    model_food.cat_id = cat_id
    model_food.name = name
    model_food.price = price
    model_food.main_image = main_image
    model_food.summary = summary
    model_food.stock = stock
    model_food.tags = tags
    model_food.updated_time = getCurrentDate()

    db.session.add(model_food)
    ret = db.session.commit()                                                                       # 修改或提交食物
    # app.logger.info( "ret:{0}".format(ret) )

    # 注意第二个参数，是变更的数量
    FoodService.setStockChangeLog( model_food.id,int(stock) - int(before_stock),"后台修改" )        # 修改库存
    return jsonify(resp)




@route_food.route( "/cat" )
def cat():
    # 分类不会太多，所以不用分页
    resp_data = {}
    req = request.values
    query = FoodCat.query
    if 'status' in req and int( req['status'] ) > -1:
        query = query.filter( FoodCat.status == int( req['status'] ) )

    list = query.order_by( FoodCat.weight.desc(),  FoodCat.id.asc() ).all()
    resp_data['list'] = list
    resp_data['current'] = 'cat'
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['search_con'] = req
    return ops_render( "food/cat.html", resp_data )

@route_food.route( "/cat-set", methods=[ 'GET', 'POST'] )               # 菜品分类的添加和编辑
def catSet():
    # 编辑和添加 —— 所以有可能有ID 有可能查不出ID
    if request.method == "GET":
        # id存在时进行编辑。不存在是进行展示。
        resp_data = {}
        req = request.args
        id = int( req.get( "id", 0 ) )
        
        info = None
        if  id:
            info = FoodCat.query.filter_by( id = id ).first()
        resp_data['info'] = info
        resp_data['current'] = 'cat'
        return ops_render( "food/cat_set.html", resp_data )
    # 获取并设置权重
    resp = { 'code': 200, 'msg': '操作成功~~', 'data':{} }
    req = request.values


    id = req['id'] if 'id' in req else 0
    name = req['name'] if 'name' in req else ''
    weight = int( req['weight'] ) if( 'weight' in req and int( req['weight'] )>0  ) else 1

    if name is None or len( name ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的分类名称"
        return jsonify( resp )
    food_cat_info = FoodCat.query.filter_by( id = id ).first()
    

    if food_cat_info:# 存在则进行编辑
        model_food_cat = food_cat_info
    else:# 不存在则进行 新建并插入
        model_food_cat = FoodCat()
        model_food_cat.created_time = getCurrentDate()
    model_food_cat.name = name
    model_food_cat.weight = weight
    model_food_cat.updated_time = getCurrentDate()

    db.session.add( model_food_cat )
    db.session.commit()
    return jsonify( resp )


@route_food.route( "/cat-ops", methods=['POST'] )       # 因为默认允许 GET方法。
def catOps():
    resp = { 'code': 200, 'msg': '操作成功~', 'data':{} }
    req = request.values
    id = req['id']  if 'id' in req else 0
    act = req['act']  if 'act' in req else ''
    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择要操作的账号~~"
        return jsonify( resp )
    
    if act not in [ 'remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~"
        return jsonify( resp )
    


    food_cat_info = FoodCat.query.filter_by( id = id ).first()
    if not food_cat_info:
        resp['code'] = -1
        resp['msg'] = "指定的分类不存在~"
        return jsonify( resp )

    # 如果存在：
    if act == "remove":
        food_cat_info.status = 0
    elif act == "recover":
        food_cat_info.status = 1
   
    food_cat_info.updated_time = getCurrentDate()
    db.session.add( food_cat_info )
    db.session.commit()
    return jsonify( resp )


