//app.js
App({
    onLaunch: function () {
        // 查找二维码链接
        var that = this;
        wx.request({
            url:  that.buildUrl( "/my/order/payimage" ),
            header: that.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    that.alert({"content": resp.msg});
                    return;
                }
                that.globalData.payCodeImage = resp.data.main_pic;
            }
        });

        var that = this;
        //  获取系统的有关信息
        wx.getSystemInfo({
            success: function (res) {
                wx.setStorageSync('systemInfo', res)
                var ww = res.windowWidth;
                var hh = res.windowHeight;
                that.globalData.ww = ww;
                that.globalData.hh = hh;
            }
        });
    },
    globalData: {
        userInfo: null,
        version: "1.0",
        shopName: "中华一番·少年心气菜馆",
        domain: "https://order.jiahaozhang.net/api",
        // domain: "http://192.168.0.105:8999/api",
        domainCode: "https://order.jiahaozhang.net/finance/pay-info",
        // domainCode: "http://192.168.0.105:8999/finance/pay-info",
        payDetailPageID: "16",
        payCodeImage: [],
        ww: 0,
        hh: 0,
    },
    tip: function (params) {
        var that = this;
        var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
        var content = params.hasOwnProperty('content') ? params['content'] : '';
        wx.showModal({
            title: title,
            content: content,
            success: function (res) {

                if (res.confirm) { //点击确定
                    if (params.hasOwnProperty('cb_confirm') && typeof (params.cb_confirm) == "function") {
                        params.cb_confirm();
                    }
                } else { //点击否
                    if (params.hasOwnProperty('cb_cancel') && typeof (params.cb_cancel) == "function") {
                        params.cb_cancel();
                    }
                }
            }
        });
    },
    alert: function (params) {
        var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
        var content = params.hasOwnProperty('content') ? params['content'] : '';
        wx.showModal({
            title: title,
            content: content,
            showCancel: false,
            success: function (res) {
                if (res.confirm) { //用户点击确定
                    if (params.hasOwnProperty('cb_confirm') && typeof (params.cb_confirm) == "function") {
                        params.cb_confirm();
                    }
                } else {
                    if (params.hasOwnProperty('cb_cancel') && typeof (params.cb_cancel) == "function") {
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    console: function (msg) {
        console.log(msg);
    },
    getRequestHeader: function () { // form data进行提交，而不是进行 json提交！
        return {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': this.getCache("token")
        };
    },
    buildUrl: function (path, params) {
        var url = this.globalData.domain + path;
        var _paramUrl = "";
        if (params) {
            _paramUrl = Object.keys(params).map(function (k) {
                return [encodeURIComponent(k), encodeURIComponent(params[k])].join("=");
            }).join("&");
            //返回的仍然是个数组  所以再Join一次！
            _paramUrl = "?" + _paramUrl;
        }
        return url + _paramUrl;
    },
    getCache: function ( key ) { //同步得到 缓存
        try {
            var value = undefined;
            value = wx.getStorageSync( key );
            if (value) {
                // Do something with return value
            }
        } catch (e) {
            // Do something when catch error
        }
        return value;
    },
    setCache: function ( key, value) { //异步设置 缓存
        wx.setStorage({
            key: key,
            data: value
        })

    },
    // 自适应图片，获取图片尺寸
    getImageSize: function( image=[], params={}, index=0 ) {
        var width = params.width,
            height = params.height,
            ratio = width / height;                             //获取到的 图片的比例
        
        // 获取屏幕宽度
        var viewWidth = wx.getSystemInfoSync().windowWidth - 60,
            viewHeight = viewWidth / ratio;
        this.console("width:"+width + ",height:"+height+",viewWidth:"+viewWidth+",viewHeight"+viewHeight);
        
        image[index] = {
            "width": viewWidth,
            "height": viewHeight,
        };
        
        return image;
    },
    // 购物车抛物线动画
    bezier: function (pots, amount) {
        var pot;
        var lines;
        var ret = [];
        var points;
        for (var i = 0; i <= amount; i++) {
          points = pots.slice(0);
          lines = [];
          while (pot = points.shift()) {
            if (points.length) {
              lines.push(pointLine([pot, points[0]], i / amount));
            } else if (lines.length > 1) {
              points = lines;
              lines = [];
            } else {
              break;
            }
          }
          ret.push(lines[0]);
        }
        function pointLine(points, rate) {
          var pointA, pointB, pointDistance, xDistance, yDistance, tan, radian, tmpPointDistance;
          var ret = [];
          pointA = points[0];//点击
          pointB = points[1];//中间
          xDistance = pointB.x - pointA.x;
          yDistance = pointB.y - pointA.y;
          pointDistance = Math.pow(Math.pow(xDistance, 2) + Math.pow(yDistance, 2), 1 / 2);
          tan = yDistance / xDistance;
          radian = Math.atan(tan);
          tmpPointDistance = pointDistance * rate;
          ret = {
            x: pointA.x + tmpPointDistance * Math.cos(radian),
            y: pointA.y + tmpPointDistance * Math.sin(radian)
          };
          return ret;
        }
        return {
          'bezier_points': ret
        };
      },

});