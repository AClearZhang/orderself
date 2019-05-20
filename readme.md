毕业设计一整套的自助订餐系统
=====================
# 即刻@少年初心
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
