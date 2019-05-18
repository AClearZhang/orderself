//map.js
//上来 显示超市位置
//返回自己的location
//trans 来回移动
const app = getApp()

var point_restautrant = {
    longitude: 116.959215,
    latitude: 36.619635,
}
var point_cover = {
    longitude: 116.96581976996528,
    latitude: 36.613567437065974
}


Page({
  data: {
    longitude:  116.959215,
    latitude: 36.619635,
    longitude_my: point_cover.longitude,
    latitude_my: point_cover.latitude,
    scale: 14,
    markers: [{
        id: 1,
        latitude: point_restautrant.latitude,
        longitude: point_restautrant.longitude,
        name: '中华一番店铺',
        iconPath: '../../images/marker_res.png'
      }],
    covers: [{
        latitude: point_cover.latitude,
        longitude: point_cover.longitude,
        iconPath: '../../images/location.png'
    }],
    isTrans: false,
  },
  onReady( e ) {
    // 使用 wx.createMapContext 获取 map 上下文
    var that = this;
    this.mapCtx = wx.createMapContext('orderMap');
    this.mapCtx.getScale( {
        success( res ) {
            that.setData( {
                scale: res.scale
            } );
        },
        fail( res ) {
            console( "getScale faild." );
        }

    });
  },
  onLoad: function () {
    var that=this;
    wx.showLoading({
      title:"定位中",
      mask:true
    });

    wx.getLocation({
      type: 'gcj02',
      altitude:true,//高精度定位
      //定位成功，更新定位结果
      success: function (res) {
        var latitude = res.latitude
        var longitude = res.longitude
        var speed = res.speed
        var accuracy = res.accuracy
       
        that.setData({
          longitude_my:longitude,
          latitude_my: latitude,
          speed: speed,
          accuracy: accuracy
        })
      },
      //定位失败回调
      fail:function(){
        wx.showToast({
          title:"定位失败",
          icon:"none"
        })
      },
 
      complete:function(){
        //隐藏定位中信息进度
        wx.hideLoading()
      }
 
    });
  },
  // map 按钮触发事件
  getCenterLocation() {
    var that = this;
    this.mapCtx.getCenterLocation({
      success(res) {
        // 设置当前cover
        var cover = {};
        cover.longitude = res.longitude;
        cover.latitude = res.latitude;

        var cover_data = that.data.covers;
        cover_data[1] = cover;
        console.log( cover_data[1].longitude );
        console.log( cover_data[1].latitude );
        that.setData({
            covers: cover_data
        });

      }
    });
    this.mapCtx.getScale( {
        success( res ) {
            that.setData( {
                scale: res.scale
            } );
        },
        fail( res ) {
            console( "getScale faild." );
        }

    });
  },
  moveToLocation() {
    this.mapCtx.moveToLocation()
  },
  translateMarker() {
    var that = this;
    if( !that.data.isTrans ){
        this.mapCtx.translateMarker({
            markerId: 1,
            autoRotate: true,
            duration: 1500,
            destination: {
              latitude: that.data.latitude_my,
              longitude: that.data.longitude_my,
            },
            success() {
              that.setData({
                  isTrans: !that.data.isTrans
              })
              console.log( "animation success." )
            },
            fail() {
              console.log( "animation fail." )
            }
          });
    }else if( that.data.isTrans ){
        this.mapCtx.translateMarker({
            markerId: 1,
            autoRotate: true,
            duration: 1500,
            destination: {
              latitude: that.data.latitude,
              longitude: that.data.longitude,
            },
            success() {
              that.setData({
                  isTrans: !that.data.isTrans
              })
              console.log( "animation success." )
            },
            fail() {
              console.log( "animation fail." )
            }
          }); 
    }
     
  },
  includePoints() {

    var that = this;
    
    this.mapCtx.includePoints({
        padding: [10],
        points: [{
            longitude: 116.96581976996528,
            latitude: 36.613567437065974
        }, {
            longitude: 116.959215,
            latitude: 36.619635,
        },{
            longitude: that.data.longitude_my,
            latitude: that.data.latitude_my,
        }]
    })
  }
})