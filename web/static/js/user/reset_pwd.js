;
// document.write("<script language=javascript src='/js/common.js'></script>");

var user_edit_ops = {
    init:function(){
        this.eventBind();

    },
    eventBind:function(){

        $("#save").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理！！请不要重复提交~~~");
                return;
            }


            var old_password = $("#old_password").val();
            var new_password = $("#new_password").val();


            // 进行有效性判断  错误
            if( !old_password ){
                common_ops.alert( "请输入原密码~" );
                return false;
            }
            
            if( !new_password || new_password.length < 6 ){
                common_ops.alert( "请输入不少于6位的新密码~" );
                return false;
            }

            btn_target.addClass("disabled");

            var data = {
                old_password: old_password,
                new_password: new_password

            };
            //ajax异步上传
            $.ajax({
                url: common_ops.buildUrl("/user/reset-pwd"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function( res ){
                    btn_target.removeClass("disabled");

                    var callback = null;
                    
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href =  window.location.href;       //统一刷新当前页面
                        }
                    }

                    common_ops.alert( res.msg, callback );                      //回调函数执行 提示.
                },
                error: function( data ){

                    btn_target.removeClass("disabled");
                    common_ops.alert( "抱歉!reset_pwd  出错了.请联系管理员：aclearzhang@qq.com" ); 
                }


            })

        });

    }


};


$(document).ready( function(){
     user_edit_ops.init();


} );




