;
var food_cat_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind: function(){
        var that = this;
        $(".wrap_search  select[name=status]").change(function(){
            $(".wrap_search").submit();                                //状态改变了则进行提交到后台 再进行提交表单、查询操作
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
                    url: common_ops.buildUrl("/food/cat-ops"),
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
                        common_ops.alert( "抱歉，food_cat_"+ act +" 出错了."+  
                         "<br>" +"请联系管理员：aclearzhang@qq.com" ); 
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
    food_cat_ops.init();
} );