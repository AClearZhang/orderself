Job 列表
======
# 使用
* python manager.py runjob -m stat/daily -a member
* python manager.py runjob -m stat/daily -a food
* python manager.py runjob -m stat/daily -a site

* python manager.py runjob -m pay/index -a fukuan
* python manager.py runjob -m pay/index -a qucan
* python manager.py runjob -m pay/index -a pinglun
* python manager.py runjob -m pay/index -a all
# 队列Job
                 <!-- 每一分 都去跑——要么发送消息模板，要么取消订单 -->
        * * * * * { . ~/.bash_jobs && cd /www/wwwproject/orderself && python manager.py runjob -m queue/index ;} >> /www/wwwproject/logs/queue_list.`date +\%Y_\%m_\%d`.log 2>&1
        
        * * * * * { . ~/.bash_jobs && cd /www/wwwproject/orderself && python manager.py runjob -m pay/index ;} >> /www/wwwproject/logs/pay_index.`date +\%Y_\%m_\%d`.log 2>&1
        1 2 * * * { . ~/.bash_jobs && cd /www/wwwproject/orderself && python manager.py runjob -m stat/daily -a member ;} >> /www/wwwproject/logs/pay_index.`date +\%Y_\%m_\%d`.log 2>&1
        2 2 * * * { . ~/.bash_jobs && cd /www/wwwproject/orderself && python manager.py runjob -m stat/daily -a food ;} >> /www/wwwproject/logs/pay_index.`date +\%Y_\%m_\%d`.log 2>&1
        3 2 * * * { . ~/.bash_jobs && cd /www/wwwproject/orderself && python manager.py runjob -m stat/daily -a site ;} >> /www/wwwproject/logs/pay_index.`date +\%Y_\%m_\%d`.log 2>&1