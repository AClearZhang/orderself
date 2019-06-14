# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from application import app, db
import re, json
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.Image import Image


route_upload = Blueprint( 'upload_page',  __name__ )



@route_upload.route( '/ueditor', methods=['GET', 'POST'] )
def ueditor():
    # 获取page页面用GET
    req = request.values
    action = req['action'] if 'action' in req else ''

    if action == "config":
        root_path = app.root_path
        # 解析JSON格式的配置文件
        # 这里使用PHP版本自带的config.json文件
        config_path = "{0}/web/static/plugins/ueditor/upload_config.json".format( root_path )
        app.logger.info( "Config_path is:" +  config_path )
        with open( config_path ) as fp:
            try:
                # 删除 `/**/` 之间的注释
                config_data = json.loads( re.sub(r'\/\*.*\*\/', '', fp.read()) )
            except:
                config_data = {}
        
        return jsonify( config_data )

    # action == uploadimage
    if action == "uploadimage":
        return  uploadImage()           # 图片上传的动作

    if action == "listimage":
        return listImage()                    # 图片展示动作

    return 'upload'

@route_upload.route('/pic', methods=['GET', 'POST'])
def uploadPic():
    # iframe上传相关域
    file_target = request.files
    app.logger.info( "/upload/pic :{}".format(file_target) )             
    upfile = file_target['pic'] if 'pic' in file_target else None
    callback_target = 'window.parent.upload'
    if upfile is None:
        return "<script type='text/javascript'>{0}.error({1})</script>".format( callback_target, "上传失败！")


    # 统一的封装上传！  因为被多处调用进行上传！封面、图片等等等————   实际操作的函数
    ret = UploadService.uploadByFile( upfile )
    if ret['code'] != 200:
        return "<script type='text/javascript'>{0}.error({1})</script>".format( callback_target, "上传失败 " + ret['msg'])
        
    # 成功
    # return  "<script type='text/javascript'>{0}.success({1})</script>".format( callback_target, ret['data']['file_key'] + "上传成功。")
    return "<script type='text/javascript'>{0}.success('{1}')</script>".format(callback_target,ret['data']['file_key'] )


# 配合ueditor 进行图片上传的动作
def uploadImage():
    # 返回json参数
    resp = { 'state':'SUCCESS', 'url':'', 'title':'', 'original':'' }
    file_target = request.files                 # 'upfile', <FileStorage : 'food.jpg'('image/jpeg')>
    app.logger.info("file_taget is:" ) 
    app.logger.info(file_target ) 
    upfile = file_target['upfile'] if 'upfile' in file_target else None
    if upfile is None:
        resp['status'] = "上传失败"
        return jsonify( resp )

    # 统一的封装上传！  因为被多处调用进行上传！封面、图片等等等————   实际操作的函数
    ret = UploadService.uploadByFile( upfile )
    if ret['code'] != 200:
        resp['state'] = "上传失败: " + ret['msg']
        return jsonify( resp )
    app.logger.info( "ret is :{0}".format( ret ) )
    resp['url'] = UrlManager.buildImageUrl( ret['data']['file_key'] )
    return jsonify( resp )

'''
返回上传的所有图片 - 方便进行在线管理 - 所以创建images数据库
'''
def listImage():
    '''
    action: listimage
    start: 0
    size: 20                返回每一页开始的ID字段 和 图片页数
    '''
    
    resp = { 'state': 'SUCCESS', 'list': [], 'start': 0, 'total': 0 }
    req = request.values
    start = int( req['start'] ) if 'start' in req else 0
    page_size = int( req['size'] ) if 'size' in req else 20

    # 分页 方法2——通过 id方式，快速查询id，跨苏查询出来结果集——更快!    
    # 分页 方法1——通过 offset：
    query = Image.query
    if start > 0:
        query = query.filter( Image.id < start )                    # 因为咱们是按照  降序排列进行查询的。


    # 获取对应list —— 图片路径的存储地址
    list = query.order_by( Image.id.desc() ).limit( page_size ).all()
    images = []

    image_id = None
    if list:
        for item in list:
            images.append( {'url':UrlManager.buildImageUrl( item.file_key ) } )
            image_id = item.id

    resp['list'] = images
    resp['start'] = image_id
    resp['total'] = len( images )
    return jsonify( resp )
