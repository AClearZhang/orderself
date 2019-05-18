;
var member_set_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind: function(){
        $(".wrap_member_set  .save").click(function(){
            var btn_taget = $(this);
            if( btn_taget.hasClass("disabled") ){
                common_ops.alert("正在处理，请不要重复提交");
                return;
            } 

            var nickname_target = $(".wrap_member_set input[name='nickname']");
            var nickname = nickname_target.val()

            if ( nickname.length < 1){
                common_ops.tip("请输入符合规范的姓名", nickname_target);
                return;
            }

            //重复处理
            btn_taget.addClass("disabled");

            //数据提交
            var data = {
                nickname: nickname,
                id: $(".wrap_member_set  input[name='id']").val()
            };
           
            $.ajax({
                url: common_ops.buildUrl("/member/set"),
                type: "POST",
                data: data,
                dataType: 'json',
                success: function(res){
                    //操作成功
                    var callback = null;
                    btn_taget.removeClass("disabled");
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href = common_ops.buildUrl("member/index");
                        }
                    }

                    common_ops.alert( res.msg, callback );

                }
            });
        });
    }


};


$(document).ready(function(){
    member_set_ops.init();
});

