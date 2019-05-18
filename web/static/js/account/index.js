;
var account_index_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind: function(){
        var that = this;
        $(".wrap_search .search").click(function(){
            $(".wrap_search").submit();
        });
        //删除
        $(".remove").click( function(){
            that.ops( "remove", $(this).attr("data") );
        } );
        //恢复
        $(".recover").click( function(){
            that.ops( "recover", $(this).attr("data") );
        } );
    },
    ops: function( act, id ){
        var callback = {
            'ok': function(){
                $.ajax({
                    url: common_ops.buildUrl("/account/ops"),
                    type: 'POST',
                    data: {
                        act: act,
                        id: id
                    },
                    dataType: 'json',
                    success: function( res ){
                        var callback = null;
                        
                        if( res.code == 200 ){
                            callback = function(){
                                window.location.href =  window.location.href;       //统一刷新当前页面
                            }
                        }
                        //callback();
                        common_ops.alert( res.msg, callback );                      //回调函数执行 提示.
                    },
                    error: function( data ){
                        common_ops.alert( "抱歉，account_"+ act +" 出错了.\n请联系管理员：aclearzhang@qq.com" ); 
                    }
        
        
                })
            },
            'cancel': function(){
                null
            }

        };
        common_ops.confirm( ( act == "remove"? "确定删除吗？" : "确定恢复吗？" ), callback );

    }


};



$(document).ready( function(){
    account_index_ops.init();
} );