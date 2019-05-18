;//调教 食品分类的JS
var food_cat_set_ops = {
    init:function(){
        this.eventBind();

    },
    eventBind:function(){

        $(".wrap_cat_set .save").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理！！请不要重复提交~~~");
                return;
            }

            // 获取相应数值
            var name_target = $(".wrap_cat_set  input[name=name]");
            var name = name_target.val();
            
            var weight_target = $(".wrap_cat_set  input[name=weight]");
            var weight = weight_target.val();
        
            // 测试
            // var uid_target = $(".wrap_account_set  input[name=id]");
            // var uid = uid_target.val();
            // console.log( "uid is :" + uid );
            
            // 进行有效性判断  错误
            if( !name || name.length < 1 ){
                common_ops.tip( "请输入符合规范的分类名称~~", name_target );
                return false;
            }
            //输入的网页字符 全部是字符串。需要将字符串转化为 number
            if( parseInt(weight) < 1 ){
                common_ops.tip( "请输入符合规范的权重，并且至少大于1。", weight_target );
                return false;
            }

            btn_target.addClass("disabled");

            var data = {
                name: name,
                weight: weight,
                id:  $(".wrap_cat_set  input[name=id]").val()
            };
            //ajax异步上传
            $.ajax({
                url: common_ops.buildUrl("/food/cat-set"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function( res ){
                    btn_target.removeClass("disabled");

                    var callback = null;
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href =  common_ops.buildUrl("/food/index");       //统一刷新当前页面
                        }
                    }

                    common_ops.alert( res.msg, callback );                      //回调函数执行 提示.
                },
                error: function( data ){

                    btn_target.removeClass("disabled");
                    common_ops.alert( "抱歉，food_cat_set  出错了.请联系管理员：aclearzhang@qq.com" ); 
                }


            })

        });

    }


};


$(document).ready( function(){
    food_cat_set_ops.init();


} );









