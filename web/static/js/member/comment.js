;
var member_comment_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind: function(){
        

        // var that = this;
        // $(".wrap_search .search").click(function(){
        //     $(".wrap_search").submit();
        // });
        // //删除
        // $(".remove").click( function(){
        //     that.ops( "remove", $(this).attr("data") );
        // } );
        // //恢复
        // $(".recover").click( function(){
        //     that.ops( "recover", $(this).attr("data") );
        // } );
    },
};



$(document).ready( function(){
    member_comment_ops.init();
} );