// //logs.js
// var util = require('../../utils/util.js')
// var sliderWidth = 190// 需要设置slider的宽度，用于计算中间位置
// // 最大行数
// var max_row_height = 5;
// // 行高
// var food_row_height = 50;
// // 底部栏偏移量
// var cart_offset = 90;
const util = require( "../../utils/util" );

var app = getApp();

Page({
  data: {

    //新增
    categories: [],
    activeCategoryId: 0,
    goods: [],
    list: [],             //购物车list
    hide_good_box: true,  // 购物车小球动画——默认隐藏
    p: 1,
    processing: false,
    loadingMoreHidden: true, //底线
  },
  onLoad: function (options) {
    // 购物车动画
    var that = this;
    var systemInfo = wx.getStorageSync('systemInfo');
    this.busPos = {};
    this.busPos['x'] = 230;//购物车的位置
    this.busPos['y'] = 551;
  },
  onShow: function () {
    var that = this;
    that.getCartList();

    // 注意新增加数据的 初始值
    that.setData({
      goods: [],
      loadingMoreHidden: true,
      p: 1,
      processing: false
    });
    that.getFoodCatList();
  },
  scrollViewLower: function( e ){
    var that = this;
    setTimeout( function(){
        that.getFoodCatList();
    }, 500);        //ms

  },
  toDetailsTap: function (e) {
    app.console( "进入munutap id:"+  e.currentTarget.dataset.id);
    wx.navigateTo({
      url: "/pages/food/info?id=" + e.currentTarget.dataset.id
    });
  },
  getFoodCatList: function () { //Food.py 里面,获取数据api
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
      url: app.buildUrl("/food/menu/list"),
      header: app.getRequestHeader(),
      data: {
        cat_id: that.data.activeCategoryId,     //选中类别
        p: that.data.p,
      },
      success: function (res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alert({
            "content": resp.msg
          });
          return;
        }

        var goods = resp.data.list;
        that.setData({
          goods: that.data.goods.concat( goods ),
          categories: resp.data.cat_list,
          p: that.data.p + 1,
          processing: false,

        });
        if( resp.data.has_more == 0 ){
          that.setData({
              loadingMoreHidden: false           //不隐藏
          });
        }

      },
      fail: function (err) {
        app.alert({
          'title': "API请求失败",
          'content': err
        });
      }
    });
  },
  catClick: function (e) {
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
    that.getFoodCatList();
  },
  // 页面index切换完成
  

  // 新增购物车数据
  getCartList: function () {
    var that = this;
    
    // 获取后端数据        
    wx.request({
        url: app.buildUrl("/cart/index"),
        header: app.getRequestHeader(),
        data: {
           id: that.data.id
        },
        success: function(res){
            // app.console('Enter the getFoodList() The P is: '+ that.data.p + ".And processing is:" + that.data.processing );
            var resp = res.data;
            
            if( resp.code != 200 ){
                app.alert( {"content": resp.msg} );
                return;
            }
            that.setData({
                // 默认参数设置  JS负责处理 初始数据、生命周期回调、事件处理函数
                list: resp.data.list,
                totalPrice: 0.00,
            });
            that.setPageData( that.totalPriceNum(), that.data.list);
        },
        fail: function(err){
            app.alert({ 'title':"API请求失败", 'content': err });
        }
    });
  },
  totalPriceNum: function () {
    var list = this.data.list;
    var totalPrice = 0.00, totalNum = 0;
    for (var i = 0; i < list.length; i++) {
        if ( !list[i].active) {
            continue;
        }
        totalPrice = totalPrice + parseFloat( list[i].price ) * list[i].number ;
    }
    totalNum = list.length;
    return [totalPrice, totalNum];
  },
  setPageData: function ( total, list) {
    this.setData({
        list: list,
        totalPrice: total[0],
        totalNum: total[1],
    });
  },

  //加数量
  jiaBtnTap: function (e) {
    var that = this;
    var food_id = e.currentTarget.dataset.id;
    var number = e.currentTarget.dataset.num + 1;

    var goods = that.data.goods;
    //var index = e.currentTarget.dataset.index;
    //var item = goods[index];
    // item.quantity = number;
    goods[e.currentTarget.dataset.index].quantity = number;
    
    that.setData({
      goods: goods
    })

    that.setCart( food_id, number );
    // 添加到购物车动画
    that.touchOnGoods(e);


    //获取当前点击位置
    // app.console( "x:"+e.detail.x+" y:"+e.detail.y )     //x:235 y:551 左上角为原点
                                                        //x:238 y:511  x:243 y:510控制点
  },
  //减数量
  jianBtnTap: function (e) {
    var that = this;
    var food_id = e.currentTarget.dataset.id;
    var number = 0;
    if ( e.currentTarget.dataset.num > 1 ){
      number = e.currentTarget.dataset.num - 1;

      var goods = that.data.goods
      // var index = e.currentTarget.dataset.index;
      // var item = goods[index];
      // item.quantity = number;
      goods[e.currentTarget.dataset.index].quantity = number;
      that.setData({
        goods: goods
      });

      that.setCart( food_id, number );
    }else if(  e.currentTarget.dataset.num == 1 ) {
      var params = {
        "title": "提示",
        "content": "请到购物车 删除商品. ：D",
        "cb_confirm": null,
      };
      app.tip( params);
    }

    //获取当前点击位置
    // app.console( "x:"+e.detail.x+" y:"+e.detail.y );     //x:235 y:551 左上角为原点
                                                        //x:238 y:511  x:243 y:510控制点
  },
  // 数据统一提交
  setCart: function( food_id, number ){
    var that = this;
    var data = {
        'id': food_id,                      // 购买食品的id
        'number': number
    };

    // 每次加减数据 都要 请求添加至后台数据库
    wx.request({
        url: app.buildUrl("/cart/set"),              // 另外添加编辑，所以重新定一个事件
        header: app.getRequestHeader(),
        method: 'POST',
        data: data,
        success: function (res) {
          that.getCartList();
          that.getFoodCatList();
        },
        fail: function (err) {
            app.alert({
                'title': "API请求失败",
                'content': err
            });
        }
    });
  },
  // 购物车小球动画准备
  touchOnGoods: function (e) {
    // 计算出三个点的坐标
    this.finger = {}; var topPoint = {};
    //点击的位置
    this.finger['x'] = e.touches["0"].clientX;
    this.finger['y'] = e.touches["0"].clientY;


    // 控制点的y的值定在低的点的上方100处
    if (this.finger['y'] < this.busPos['y']) {
      topPoint['y'] = this.finger['y'] - 100;
    } else {
      topPoint['y'] = this.busPos['y'] - 100;
    }
    topPoint['x'] = Math.abs(this.finger['x'] - this.busPos['x']) / 2;

    // 控制点确保x在电击点和购物车之间
    if (this.finger['x'] > this.busPos['x']) {
      topPoint['x'] = (this.finger['x'] - this.busPos['x']) / 2 + this.busPos['x'];
    } else {
      topPoint['x'] = (this.busPos['x'] - this.finger['x']) / 2 + this.finger['x'];
    }

    // 传给bezier 
    this.linePos = app.bezier([this.busPos, topPoint, this.finger], 30);
    this.startAnimation(e);
  },// 动画开始
  startAnimation: function (e) {
    var index = 0, that = this,
      bezier_points = that.linePos['bezier_points'];

    this.setData({
      hide_good_box: false,
      bus_x: that.finger['x'],
      bus_y: that.finger['y']
    })
    var len = bezier_points.length;
    index = len
    this.timer = setInterval(function () {
      for(let i = index - 1; i > -1; i--) {
        that.setData({
          bus_x: bezier_points[i]['x'],
          bus_y: bezier_points[i]['y']
        })

        if (i < 1) {
          clearInterval(that.timer);
          // that.addGoodToCartFn(e);
          that.setData({
            hide_good_box: true
          })
        }
      }
    }, 25);
  },

})