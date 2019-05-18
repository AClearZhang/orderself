var app = getApp();
Page({
    data: {
        pay_image: [],
        images_size: [],
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            order_sn: e.order_sn,
            pay_image: app.globalData.payCodeImage
        });
    },
    onShow: function () {
        this.getPayOrderInfo();
        // that.setData({
        //     info: {
        //         order_sn:"123123",
        //         status: -8,
        //         status_desc: "待支付",
        //         deadline:"2018-07-31 12:00",
        //         pay_price: "85.00",
        //         yun_price: 0.00,
        //         total_price: "85.00",
        //         address: {
        //             name: "少年初心",
        //             mobile: "12345678901",
        //             address: "山东省济南XX"
        //         },
        //         goods: [
        //             {
        //                 name: "小鸡炖蘑菇",
        //                 price: "85.00",
        //                 unit: 1,
        //                 pic_url: "/images/food.jpg"
        //             },
        //             {
        //                 name: "小鸡炖蘑菇",
        //                 price: "85.00",
        //                 unit: 1,
        //                 pic_url: "/images/food.jpg"
        //             }
        //         ]
        //     }
        // });
    },
    getPayOrderInfo:function(){
        var that = this;
        wx.request({
            url: app.buildUrl("/my/order/info"),
            header: app.getRequestHeader(),
            data: {
                order_sn: that.data.order_sn
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                   info: resp.data.info
                });
            }
        });
    },
    goToIndex: function() {
        var that = this;
        wx.switchTab({
            url: "/pages/food/index"
        });

    },
    imageLoad: function( e ) {
        // 每次图片加载的时候，执行
        var that = this;
        var image = app.getImageSize( that.data.images_size, e.detail, e.target.dataset.index);
        that.setData({
            images_size: image
        })
        //app.console( "width:"+image[0].width+",height:"+image[0].height );
    }
});