# 用户逻辑操作包！
import hashlib, requests, random, string, json
from application import app


class MemberService():

    # 生成cookie授权码
    @staticmethod
    def geneAuthCode( member_info ):
        m = hashlib.md5()
        str = "%s-%s-%s" %( member_info.id, member_info.salt, member_info.status )
        m.update( str.encode("utf-8") )
        return m.hexdigest()

    @staticmethod
    def geneSalt( length = 16 ):
        keylist = [random.choice( string.ascii_letters + string.digits )  for i in range( length )]
        return ( "".join(keylist) )

    @staticmethod
    def getWeChatOpenid( code ):
        # 下面通过code 获取用户的一些基本信息，以及+ appid  获得用户唯一的openid标致！
        # 方便进行  用户是否已经注册的！  数据库比照的判定！所以会员 一定要有自己的数据库!
        # 发送 get请求
        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code".format( app.config['MINA_APP']['appid'], app.config['MINA_APP']['appkey'], code)  
        # 安装request扩展
        r = requests.get( url )
        res = json.loads( r.text )
        # app.logger.info( "The result RES is:{0} and The result R.Text is:{1} ".format( res, r.text ))
        openid = res['openid'] if 'openid' in res else None                # 获取用户唯一表示 
        return openid
