from werkzeug.utils import secure_filename 
from application import app, db
from common.libs.Helper import getCurrentDate
from common.models.Image import Image
import os, stat, uuid

class UploadService():
    @staticmethod
    def uploadByFile( file ):
        config_upload = app.config['UPLOAD']
        resp = { 'code': 200, 'msg': '操作成功~', 'data': {} }
        # 获取文件相关属性  一致？
        filename = secure_filename( file.filename )         # 获取安全的文件名称
        ext = filename.split(".", 1)[1]

        # 扩展名是否 一致
        if ext not in config_upload['ext']:
            # 报错
            resp['code'] = -1
            resp['msg'] = "不允许的扩展类型文件~"
            return resp

        # 上传过程
        # 保证文件目录存在
        root_path = app.root_path + config_upload['prefix_path']
        # 文件夹名称
        file_dir = getCurrentDate( "%Y%m%d" )
        save_dir = root_path + file_dir
        # 判断路径是否存在
        if not os.path.exists( save_dir ):
            os.mkdir( save_dir )
            os.chmod( save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)         # 文件夹有 777权限
        
        # 文件名称—— uuid生成全局不重复的唯一的 文件名称
        file_name = str( uuid.uuid4() ).replace( "-", "" ) + "." + ext
        file.save( "{0}/{1}".format( save_dir, file_name ) )                        # 存储文件—— 路径+文件名称
        
        # 存储image
        model_Image = Image()
        model_Image.file_key = file_dir + "/" + file_name
        model_Image.created_time = getCurrentDate()
        db.session.add( model_Image )
        db.session.commit()

        # resp['data'] = {
        #     'file_key': file_dir + "/" + file_name
        # }
        resp['data']['file_key'] = model_Image.file_key
        return resp
