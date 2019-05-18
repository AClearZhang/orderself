# -*- coding: utf-8 -*-  
# 入口文件
from application import app,manager
from flask_script import Server
import www
from jobs.launcher import runJob


# manager 进行封装和 特殊处理

## web server
manager.add_command("runserver", Server( host='0.0.0.0', port=app.config['SERVER_PORT'], use_debugger = True, use_reloader = True))

## 添加 Job启动服务
manager.add_command( "runjob", runJob() )       # 方法runJob()

def main():
    # app.run( host='0.0.0.0', debug= True )
    print("Hello This is Test.")
    print("Root_path is :%s" % app.root_path)
    manager.run()

if __name__ == '__main__':       #这里为 入口方法
    try:
        import sys
        print("This is __name__")
        sys.exit( main() )

    except Exception as e:
        import traceback
        traceback.print_exc()

# from application import app,manager
# from flask_script import Server
# import www

# ##web server
# manager.add_command( "runserver", Server( host='0.0.0.0',port=app.config['SERVER_PORT'],use_debugger = True ,use_reloader = True) )

# def main():
#     manager.run( )

# if __name__ == '__main__':
#     try:
#         import sys
#         sys.exit( main() )
#     except Exception as e:
#         import traceback
#         traceback.print_exc()