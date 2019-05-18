
'''
    微信支付与拉起支付 —— 保留接口，未申请到商家认证

    直接使用二维码付款，通过后台进行 订单的管理
'''

class WeChatService():
    def __init__( self ):
        pass

    def create_sign( self, pay_data = None )
        '''
            产生签名
            :param pay_data:
            : return  :
        '''
        stringA = "&".join( [ "{0}={1}".format( k, pay_data.get( k ) ) for k in sorted( pay_data ) ])
        stringSignTemp = '{0}&key={1}'.format( stringA,  )



    # 获取下单数据
    def get_pay_info( self, pay_data = None ):
        '''
            获取支付信息
        '''
        # 统一下单


