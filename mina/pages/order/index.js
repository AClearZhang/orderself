//获取应用实例
var app = getApp();

Page({
    data: {
        goods_list: [],
        default_address:null,
        yun_price: "0.00",
        pay_price: "0.00",
        total_price: "0.00",
        params: null,
        curMethod: "0",               //到店 快递
        express_address_id:0,         //收货地址
        note: '',                     //用户的备注
    },
    onShow: function () {
        var that = this;
        that.getOrderInfo();
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            params: JSON.parse( e.data )
        });
    },
    // 提交订单。商品数据+备注信息 发送到后台去！
    createOrder: function (e) {
        wx.showLoading();
        var that = this;

        var data = {
            eat_method: that.data.curMethod,
            type: that.data.params.type,
            goods: JSON.stringify(that.data.params.goods),
            express_address_id: that.data.default_address.id,
            note: that.data.note
        };
        // 并发——购物车：并发删除单表 + 去后台的库存 + 添加到我的单页列表； 如果是直接购买 直接去库存 + 添加到我的单页列表就好
        wx.request({
            url: app.buildUrl("/order/create"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success: function(res){
                wx.hideLoading();                               // 隐藏cart界面的 loading条
                var resp = res.data;
                if( resp.code != 200 ){
                    app.alert( {"content": resp.msg} );
                    return;
                }

                wx.navigateTo({
                    url: "/pages/my/order_list"                 // 直接重定向到my界面
                });
            }

        });
        
       
    },
    addressSet: function () {
        wx.navigateTo({
            url: "/pages/my/addressSet"
        });
    },
    selectAddress: function () {
        wx.navigateTo({
            url: "/pages/my/addressList"
        });
    },
    getOrderInfo: function(){   
        var that = this;
        var data = {
            type: that.data.params.type,
            goods: JSON.stringify(that.data.params.goods),
        };

        // 后台发送请求，因为GET 获取不到这么大的数据量。所以使用POST
        wx.request({
            url: app.buildUrl("/order/info"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success: function(res){
                var resp = res.data;
                if( resp.code != 200 ){
                    app.alert( {"content": resp.msg} );
                    return;
                }

                that.setData({
                    goods_list: resp.data.food_list,
                    default_address: resp.data.default_address,
                    pay_price: resp.data.pay_price,
                    yun_price: resp.data.yun_price,
                    total_price: resp.data.total_price
                });

                if( that.data.default_address ){
                    that.setData({
                         express_address_id: that.data.default_address.id
                    });
                }
            }

        });

    },
    changeEatMethod: function(e){
        var that = this;
        var index = e.currentTarget.dataset.index;
        that.setData({
            curMethod: index
        });
    },
    getNote: function( e ) {
        var that = this;
        var note = e.detail.value;
        that.setData({
            note: note
        });
        
    }

});
