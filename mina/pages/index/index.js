//login.js
//获取应用实例
var app = getApp();
Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {},
    regFlag: true
  },
  goToIndex: function () {
    wx.switchTab({
      url: '/pages/food/index',
    });
  },
  onLoad: function () { // 小程序 生命周期,加载完成之后  进行登录
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
    //this.login();
    this.checkLogin();
  },
  onShow: function () {

  },
  onReady: function () {
    var that = this;
    setTimeout(function () {
      that.setData({
        remind: ''
      });
    }, 1000);
    wx.onAccelerometerChange(function (res) {
      var angle = -(res.x * 30).toFixed(1);
      if (angle > 14) {
        angle = 14;
      } else if (angle < -14) {
        angle = -14;
      }
      if (that.data.angle !== angle) {
        that.setData({
          angle: angle
        });
      }
    });
  },
  checkLogin: function(){
    var that = this;
    wx.login({
      success: function ( res ) {
        // app.console( res );
        if (!res.code) {
          app.alert({
            'content': "登录失败，请再次点击~~"
          });
          return;
        }

        //登陆成功  查找数据库是否存在openid
        wx.request({
          url: app.buildUrl( "/member/check-reg" ),
          method: "POST",
          header: app.getRequestHeader(),
          data: { code: res.code },
          success: function (res) {
            app.console( res );
            // app.console( "Res code is: " + res.data.code );
            //通过code 获得openid，检查登录是否有问题.
            if( res.data.code != 200 ){
              // app.console( "登录有问题" )
              that.setData( {
                regFlag: false
              } );
              return;
            }
            app.setCache( 'token', res.data.data.token )
            that.goToIndex();
          }
        });
      }

    })

  },
  login: function (e) { // 进行登录
    var that = this;
    // app.console( e );
    if (!e.detail.userInfo) {
      app.alert({
        'content': "登录失败，请再次点击~~"
      })
      return;
    }

    // 授权成功  返回后端
    var data = e.detail.userInfo;
    wx.login({
      success: function ( res ) {
        if (!res.code) {
          app.alert({
            'content': "登录失败，请再次点击~~"
          });
          return;
        }

        data['code'] = res.code;
        //登陆成功
        wx.request({
          url: app.buildUrl( "/member/login" ),
          method: "POST",
          header: app.getRequestHeader(),
          data: data,
          success: function (res) {
            //判断有没有登录.   此时为未登录状态
            if( res.data.code != 200 ){
              // app.console( "登录有问题" )
              app.alert( { 'content': res.data.msg } );
              return;
            }
            app.setCache( 'token', res.data.data.token )
            that.goToIndex();
          }
        });
      }

    });
  },


});