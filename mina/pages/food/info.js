//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');
var utils = require('../../utils/util.js');

Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
        hideShopPopup: true,                // 隐藏添加购物车pop
        buyNumber: 1,
        buyNumMin: 1,
        buyNumMax: 1, // 允许购物的最大数量 ——  库存
        canSubmit: false, //  选中时候是否允许加入购物车
        shopCarInfo: {},
        shopType: "addShopCar", //购物类型，加入购物车或立即购买，默认为加入购物车,
        id: 0,
        shopCarNum: 4,
        commentCount: 2
    },
    onLoad: function (e) {
        var that = this;
        // app.console( e );
        that.setData({
            id: e.id
        });

        //     commentList: [
        //         {
        //             "score": "好评",
        //             "date": "2017-10-11 10:20:00",
        //             "content": "非常好吃，一直在他们加购买",
        //             "user": {
        //                 "avatar_url": "/images/more/logo.jpg",
        //                 "nick": "angellee 🐰 🐒"
        //             }
        //         },
        //         {
        //             "score": "好评",
        //             "date": "2017-10-11 10:20:00",
        //             "content": "非常好吃，一直在他们加购买",
        //             "user": {
        //                 "avatar_url": "/images/more/logo.jpg",
        //                 "nick": "angellee 🐰 🐒"
        //             }
        //         }
        //     ]
    },
    onShow: function () {
        var that = this;
        // app.console( "info.js  界面onShow（）ing……" );
        that.getInfo();
        that.getComments();
    },
    goShopCar: function () {
        wx.reLaunch({
            url: "/pages/cart/index"
        });
    },
    toAddShopCar: function () {
        this.setData({
            shopType: "addShopCar"
        });
        this.bindGuiGeTap();
    },
    tobuy: function () {
        this.setData({
            shopType: "tobuy"
        });
        this.bindGuiGeTap();
    },
    addShopCar: function () {
        var that = this;
        var data = {
            'id': that.data.info.id,                      // 购买食品的id
            'number': that.data.buyNumber
        };

        // 请求添加至后台数据库
        wx.request({
            url: app.buildUrl("/cart/set"),              // 另外添加编辑，所以重新定一个事件
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success: function (res) {
               var resp = res.data;
               app.alert( { 'content': resp.msg } );
               that.setData({
                    hideShopPopup: true                  // 隐藏出现的弹窗
               });
            },
            error: function (err) {
                app.alert({
                    'title': "API请求失败",
                    'content': err
                });
            }
        });
    },
    buyNow: function () {
        var that = this;
        var data = {
            type: "info",
            goods: [{
                "id": that.data.info.id,
                "price": that.data.info.price,
                "number": that.data.buyNumber,
            }]
        };
        that.setData({
            hideShopPopup: true
        });
        wx.navigateTo({
            url: "/pages/order/index?data=" + JSON.stringify( data )
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false
        })
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true
        })
    },
    numJianTap: function () {
        if (this.data.buyNumber <= this.data.buyNumMin) {
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum--;
        this.setData({
            buyNumber: currentNum
        });
    },
    numJiaTap: function () {
        if (this.data.buyNumber >= this.data.buyNumMax) {
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum++;
        this.setData({
            buyNumber: currentNum
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    getInfo: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/food/info"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({
                        "content": resp.msg
                    });
                    return;
                }
                that.setData({
                    info: resp.data.info,
                    buyNumMax: resp.data.info.stock,
                    shopCarNum: resp.data.cart_number,
                });
                //app.console( "购物车中数量为：" + that.data.shopCarNum );
                // 统一渲染处理 商品介绍
                WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);

            },
            error: function (err) {
                app.alert({
                    'title': "API请求失败",
                    'content': err
                });
            }
        });
    },
    /**对应参数 
     * title	转发标题	当前小程序名称	
     * path	转发路径	当前页面 path ，必须是以 / 开头的完整路径 
     * 
     * 注意此处是 前端 open-type share 直接触发——onShareAppMessage的.
    */
    onShareAppMessage: function() {
        var that = this;
        return {
            title: that.data.info.name,
            path: '/pages/food/info?id=' + that.data.info.id,               // ？？？
            success: function() {
                // 转发成功  // 写入 记录转发次数
                wx.request({
                    url: app.buildUrl("/member/share"),
                    header: app.getRequestHeader(),
                    method: 'POST',                         // 因为要写入数据库
                    data: {
                        url: utils.getCurrentPageUrlWithArgs()
                    },
                    success: function (res) {
                        var resp = res.data;
                        if (resp.code != 200) {
                            app.alert({
                                "content": resp.msg
                            });
                            return;
                        }
        
                    },
                    error: function (err) {
                        app.alert({
                            'title': "API请求失败",
                            'content': err
                        });
                    }
                });
            },
            fail: function() {
                //转发失败
            }
        }
    },
    getComments:function(){
        var that = this;
        wx.request({
            url: app.buildUrl("/food/comments"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                    commentList: resp.data.list,
                    commentCount: resp.data.count,
                });
            }
        });
    },
});