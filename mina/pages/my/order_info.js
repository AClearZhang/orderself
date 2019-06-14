var QR = require("../../utils/qrcode.js");
var app = getApp();
Page({
    data: {
        pay_image: [],
        images_size: [],
        imagePath:'',
        info: {},
        id: 0,
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            order_sn: e.order_sn,
            pay_image: app.globalData.payCodeImage,
            imagePath: '',
        });
    },
    onShow: function () {
        this.getPayOrderInfo();
        // this.getTakeCode();
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
    getTakeCode: function(){
        var that = this;
        //绘制二维码
        var size = that.setCanvasSize();//动态设置画布大小
        var url = app.globalData.domainCode +"?id=" + that.data.id;
        that.createQrCode(url,"mycanvas",size.w,size.h);
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
                   info: resp.data.info,
                   id: resp.data.info.id,
                });
                
                //绘制二维码
                var size = that.setCanvasSize();//动态设置画布大小
                app.console("id setdata is: " + that.data.id);
                var url = app.globalData.domainCode +"?id=" + that.data.id;
                that.createQrCode(url,"mycanvas",size.w,size.h);
                // app.console("id setdata is: " + that.data.id);
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
    },
    //新增
    //适配不同屏幕大小的canvas
    setCanvasSize:function(){
        var size={};
        try {
            var res = wx.getSystemInfoSync();
            var scale = 750/686;//不同屏幕下canvas的适配比例；设计稿是750宽
            var width = res.windowWidth/scale;
            var height = width;//canvas画布为正方形
            size.w = width;
            size.h = height;
            } catch (e) {
            // Do something when catch error
            console.log("获取设备信息失败"+e);
            } 
        return size;
    } ,
    createQrCode:function(url,canvasId,cavW,cavH){
        //调用插件中的draw方法，绘制二维码图片
        QR.qrApi.draw(url,canvasId,cavW,cavH);
        var that = this;
        //二维码生成之后调用canvasToTempImage();延迟3s，否则获取图片路径为空
        var st = setTimeout(function(){
            that.canvasToTempImage();
            clearTimeout(st);
        },3000);

    },
    //获取临时缓存照片路径，存入data中
    canvasToTempImage:function(){
        var that = this;
        wx.canvasToTempFilePath({
            canvasId: 'mycanvas',
            success: function (res) {
                var tempFilePath = res.tempFilePath;
                console.log(tempFilePath);
                that.setData({
                    imagePath:tempFilePath,
                });
            },
            fail: function (res) {
                console.log(res);
            }
        });
    },
    //点击图片进行预览，长按保存分享图片
    previewImg:function(e){
        var img = encodeURI(this.data.imagePath);
        wx.previewImage({
            current: img, // 当前显示图片的http链接
            urls: [img] // 需要预览的图片http链接列表
        })
    },
});