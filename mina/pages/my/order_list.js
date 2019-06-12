var app = getApp();
Page({
    data: {
        order_list: [],
        statusType: ["待付款", "待审核", "取餐号", "待评价", "已完成","已关闭"],
        status:[ "-8","-7","-6","-5","1","0" ],
        currentType: 0,
        tabClass: ["", "", "", "", "", ""]
    },
    statusTap: function (e) {
        var curType = e.currentTarget.dataset.index;
        this.setData({
            currentType: curType
        });
        this.getPayOrder();
    },
    orderDetail: function (e) {
        wx.navigateTo({
            url: "/pages/my/order_info?order_sn=" + e.currentTarget.dataset.id
        })
    },
    onLoad: function ( e ) {
        // 生命周期函数--监听页面加载
        var that = this;
        that.setData({
            currentType: e.current
        });

    },
    onReady: function () {
        // 生命周期函数--监听页面初次渲染完
    },
    onShow: function () {
        var that = this;

        that.getPayOrder();
    },
    getPayOrder: function() {
        var that = this;
        // 获取 不同页面的数据        
        wx.request({
            url: app.buildUrl("/my/order"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: {
               status: that.data.status[ that.data.currentType ],
            },
            success: function(res){
                // app.console('Enter the getFoodList() The P is: '+ that.data.p + ".And processing is:" + that.data.processing );
                var resp = res.data;
                
                if( resp.code != 200 ){
                    app.alert( {"content": resp.msg} );
                    return;
                }

                that.setData({
                    order_list: resp.data.order_list
                });
               
            },
            fail: function(err){
                app.alert({ 'title':"API请求失败", 'content': err });
            }
        });


    },
    toPay: function( e ) { 
        //将order_sn 传递到后台
        var that = this;
        // 获取 不同页面的数据        
        wx.request({
            url: app.buildUrl("/order/pay"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: {
               order_sn: e.currentTarget.dataset.id
            },
            success: function(res){
                // app.console('Enter the getFoodList() The P is: '+ that.data.p + ".And processing is:" + that.data.processing );
                var resp = res.data;
                
                // 获取微信二维码，显示在页面之上
                if( resp.code != 200 ){
                    app.alert( {"content": resp.msg} );
                    return;
                }

                wx.navigateTo({
                    url: "/pages/food/info?id=" + app.globalData.payDetailPageID
                });

            },
            fail: function(err){
                app.alert({ 'title':"API请求失败", 'content': err });
            }
        });


    },
    // 确认取餐
    orderConfirm:function( e ){
        this.orderOps( e.currentTarget.dataset.id,"confirm","确定取餐？" );
    },
    // 确认评论
    orderComment:function( e ){
        wx.navigateTo({
            url: "/pages/my/comment?order_sn=" + e.currentTarget.dataset.id
        });
    },
    // 取消订单
    orderCancel: function( e ) {
        this.orderOps( e.currentTarget.dataset.id,"cancel","确定取消订单？" );
    },
    orderOps:function(order_sn,act,msg){
        var that = this;
        var params = {
            "content":msg,
            "cb_confirm":function(){
                wx.request({
                    url: app.buildUrl("/order/ops"),
                    header: app.getRequestHeader(),
                    method: 'POST',
                    data: {
                        order_sn: order_sn,
                        act:act
                    },
                    success: function (res) {
                        var resp = res.data;
                        app.alert({"content": resp.msg});
                        if ( resp.code == 200) {
                            that.getPayOrder();
                        }
                    }
                });
            }
        };
        app.tip( params );
    }
})
