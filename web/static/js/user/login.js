;
// document.write("<script language=javascript src='../common.js'></script>");

// 第一行进行分割  防止在多行代码中js出错！   重复使用+js+后台
var user_login_ops = {
    init:function(){
        // init 方法是提供给外部访问的.
        this.eventBind();

    },
    eventBind:function(){
        $(".login_wrap .do-login").click(function(){
            // 防止重复点击 button
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理！！请不要重复提交~~~");
                return;
            }

            // 获取表单值 jQuery
            var login_name = $(".login_wrap input[name=login_name]").val();
            var login_pwd = $(".login_wrap input[name=login_pwd]").val();
            
            if( login_name == undefined || login_name.length < 1 ){
                common_ops.alert("请输入正确的登录用户名！~~~");
                return;
            }
            if( login_pwd == undefined || login_pwd.length < 1 ){
                common_ops.alert("请输入正确的登录密码！~~~");
                return;
            }
            
            btn_target.addClass("disabled");

            // 参数合法后  - 进行ajax提交
            // 链接统一管理的方法
            $.ajax({
                url: common_ops.buildUrl( "/user/login" ),
                type: "POST",
                data: {'login_name': login_name,'login_pwd': login_pwd},
                dataType: 'json',
                success: function( res ){
                    btn_target.removeClass("disabled");

                    var callback = null;
                    
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href = common_ops.buildUrl("/", null);
                        }
                    }

                    common_ops.alert( res.msg, callback );                      //回调函数执行.
                },
                error: function( data ){
                    console.log("提交请求错误！~");
                    console.log("login_name:" + login_name + "; login_pwd:" + login_pwd + ";"); 
                    console.log( data );

                    btn_target.removeClass("disabled");
                    common_ops.alert( "抱歉，出错了.请联系管理员：aclearzhang@qq.com" ); 
                }
                
            });

        });
    }


}



$(document).ready( function(){
    user_login_ops.init();


} );

