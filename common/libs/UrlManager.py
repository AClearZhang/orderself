# -*- coding: utf-8 -*-
# 对应于 链接管理器？   版本管理器？
from application import app

class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def buildUrl( path ):
        return path

    @staticmethod
    def buildStaticUrl(path):
        ver = "%s"%( 22222222 )
        path =  "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl( path )

    @staticmethod
    def buildImageUrl( path ):
        app_config = app.config['APP']
        url = app.config['APP']['domain'] + app.config['UPLOAD']['prefix_url'] + path
        return url
