;
// document.write("<script language=javascript src='/js/common.js'></script>");

var user_edit_ops = {
    init:function(){
        this.eventBind();

    },
    eventBind:function(){

        $(".user_edit_wrap .save").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理！！请不要重复提交~~~");
                return;
            }


            var nickname_target = $(".user_edit_wrap  input[name=nickname]");
            var nickname = nickname_target.val();

            var email_target = $(".user_edit_wrap  input[name=email]");
            var email = email_target.val();
            
            // 进行有效性判断  错误
            if( !nickname || nickname.length < 2 ){
                common_ops.tip( "请输入符合规范的姓名", nickname_target );
                return false;
            }
            
            if( !email || email.length < 2 ){
                common_ops.tip( "请输入符合规范的邮箱", email_target );
                return false;
            }

            btn_target.addClass("disabled");



            var data = {
                email: email,
                nickname: nickname

            };
            //ajax异步上传
            $.ajax({
                url: common_ops.buildUrl("/user/edit"),
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
                    common_ops.alert( "抱歉，user_edit  出错了.请联系管理员：aclearzhang@qq.com" ); 
                }


            })

        });

    }


};


$(document).ready( function(){
     user_edit_ops.init();


} );




