毕业设计一整套的自助订餐系统
=====================
## 即刻@少年初心
## 系统环境
* centos7  
* nginx + uwsgi + flask运行环境
* 毕设加一整套的web管理后台 和 小程序前端系统

## 启动
* `export ops_config=local|production && python manage.py runserver`

## uwsgi
* `uwsgi --ini uwsgi.ini`
* `uwsgi --stop uwsgi.ini`

## flask-sqlacodegen
* `flask-sqlacodegen 'mysql://root:123456@127.0.0.1/food_db' --outfile "common/models/model.py"  --flask`
* `flask-sqlacodegen 'mysql://root:123456@127.0.0.1/food_db' --tables user --outfile "common/models/user.py"  --flask`

## 需要添加'config'
* config包有三个文件
* 详情见  docs/config.md

## 可参考资料
* [python-Flask（jinja2）语法：过滤器](https://www.jianshu.com/p/3127ac233518)
* [SQLAlchemy 各种查询语句写法](https://wxnacy.com/2017/08/14/python-2017-08-14-sqlalchemy-filter/)
* [免费好用-为网站添加https支持](https://fanzheng.org/archives/21)
