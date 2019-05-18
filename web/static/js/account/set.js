;
// document.write("<script language=javascript src='/js/common.js'></script>");

var account_set_ops = {
    init:function(){
        this.eventBind();

    },
    eventBind:function(){

        $(".wrap_account_set .save").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理！！请不要重复提交~~~");
                return;
            }


            var nickname_target = $(".wrap_account_set  input[name=nickname]");
            var nickname = nickname_target.val();
            
            var mobile_target = $(".wrap_account_set  input[name=mobile]");
            var mobile = mobile_target.val();
            
            var email_target = $(".wrap_account_set  input[name=email]");
            var email = email_target.val();

            var login_name_target = $(".wrap_account_set  input[name=login_name]");
            var login_name = login_name_target.val();
            
            var login_pwd_target = $(".wrap_account_set  input[name=login_pwd]");
            var login_pwd = login_pwd_target.val();
            
            // 测试
            // var uid_target = $(".wrap_account_set  input[name=id]");
            // var uid = uid_target.val();
            // console.log( "uid is :" + uid );
            
            // 进行有效性判断  错误
            if( !nickname || nickname.length < 2 ){
                common_ops.tip( "请输入符合规范的姓名", nickname_target );
                return false;
            }
            if( mobile.length < 11 ){
                common_ops.tip( "请输入符合规范的手机号", mobile_target );
                return false;
            }
            
            if( !email || email.length < 1 ){
                common_ops.tip( "请输入符合规范的邮箱", email_target );
                return false;
            }
            if( login_name.length < 1 ){
                common_ops.tip( "请输入符合规范的登录名", login_name_target );
                return false;
            }
            if( login_pwd.length < 6 ){
                common_ops.tip( "请输入符合规范的密码", login_pwd_target );
                return false;
            }

            btn_target.addClass("disabled");



            var data = {
                nickname: nickname,
                mobile: mobile,
                email: email,
                login_name: login_name,
                login_pwd: login_pwd,
                id:  $(".wrap_account_set  input[name=id]").val()
            };
            //ajax异步上传
            $.ajax({
                url: common_ops.buildUrl("/account/set"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function( res ){
                    btn_target.removeClass("disabled");

                    var callback = null;
                    
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href =  common_ops.buildUrl("/account/index");       //统一刷新当前页面
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
    account_set_ops.init();


} );




