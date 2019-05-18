//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 3000,
        duration: 1000,
        loadingHidden: false, // loading
        swiperCurrent: 0,
        categories: [],
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,        // 显示哥是否有底线的内容
        searchInput: '',
        p: 1,
        processing: false 
    },
    onLoad: function () {
        var that = this;

        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });
        
    },
    onShow: function() {
        var that = this;
        that.getBannerAndCat();
    },
    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
	listenerSearchInput:function( e ){
	        this.setData({
	            searchInput: e.detail.value
	        });
	 },
	toSearch:function( e ){
	        this.setData({
	            p:1,
	            goods:[],
	            loadingMoreHidden:true
	        });
	        this.getFoodList();
	},
    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/food/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
    toDetailsTap: function (e) {
        wx.navigateTo({
            url: "/pages/food/info?id=" + e.currentTarget.dataset.id
        });
    },
    getBannerAndCat: function() {          //获取数据api
        var that = this;
        wx.request({
            url: app.buildUrl("/food/index"),
            header: app.getRequestHeader(),
            success: function(res){
                var resp = res.data;
                if( resp.code != 200 ){
                    app.alert( {"content": resp.msg} );
                    return;
                }
                that.setData({
                    banners: resp.data.banner_list,
                    categories: resp.data.cat_list
                })
                
                //同时要获取 全部的food list
                that.getFoodList();

            },
            error: function(err){
                app.alert({ 'title':"API请求失败", 'content': err });
            }
        });
    },
    catClick: function(e){
        //得到选中分类  设置选中值
        var that = this;
        that.setData({
            activeCategoryId: e.currentTarget.id
        });

        // 注意新增加数据的 初始值
        that.setData({
            goods: [],
            loadingMoreHidden: true,
            p: 1,
            processing: false
        });
        // 重新获取 food列表
        that.getFoodList();
    },
    onReachBottom: function(){
        var that = this;
        setTimeout( function(){
            that.getFoodList();
        }, 500);        //ms

    },
    getFoodList: function() {
        var that = this;
        //正在 处理则不能再请求
        if( that.data.processing ){
            app.console( "1" );
            return ;
        }
        //后续没有数据了
        if( !that.data.loadingMoreHidden ){
            app.console( "2" );
            return;
        }

        //processing
        that.setData({
            processing: true
        });

        wx.request({
            url: app.buildUrl("/food/search"),
            header: app.getRequestHeader(),
            data: {
                cat_id: that.data.activeCategoryId,     //选中类别
                mix_kw: that.data.searchInput,          //搜索框的内容
                p: that.data.p,
            },
            success: function(res){
                // app.console('Enter the getFoodList() The P is: '+ that.data.p + ".And processing is:" + that.data.processing );
                var resp = res.data;
                
                if( resp.code != 200 ){
                    app.alert( {"content": resp.msg} );
                    return;
                }
                
                var goods = resp.data.list;
                that.setData({
                    goods: that.data.goods.concat( goods ),
                    p: ( that.data.p + 1 ),
                    processing: false                       // processing   p为后端分页处理
                });

                if( resp.data.has_more == 0 ){
                    that.setData({
                        loadingMoreHidden: false           //不隐藏
                    });
                }


            },
            error: function(err){
                app.alert({ 'title':"API请求失败", 'content': err });
            }
        })
    },
});
