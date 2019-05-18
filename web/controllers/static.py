
from flask import Blueprint, send_from_directory
from application import app

# 只在自己开发的时候用， 线上部署阿里云、腾信云  并不能这么用！

route_static = Blueprint( 'static', __name__ )
@route_static.route( "/<path:filename>" )
def index( filename ):
    # app.logger.info("Filename is:{}".format(filename) )
    return send_from_directory( app.root_path + '/web/static/',  filename )



