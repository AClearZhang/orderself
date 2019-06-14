//获取应用实例
var app = getApp();
Page({
    data: {
        order_sn: null,
        user_info: null,
        order_info: null
    },
    onLoad( e ) {

    },
    onShow() {
        this.getInfo();
    },
    getInfo: function() {
        var that = this;
        that.setData({
            order_sn: null
        });

        wx.request({
            url: app.buildUrl("/member/info"),
            header: app.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
                that.setData({
                   user_info:resp.data.info,
                   order_info: resp.data.order_info,
                   order_sn: resp.data.order_info.order_sn,
                });     
            }
        });

    },
    orderDetail: function () {
        var that = this;
        if ( !that.data.order_sn ){
            wx.navigateTo({
                url: "/pages/my/order_list?current=2"
            });
        }else{
            wx.navigateTo({
                url: "/pages/my/order_info?order_sn=" + that.data.order_sn
            });
        }
        
    },
});