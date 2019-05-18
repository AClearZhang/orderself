;
/**
 * 画图通用组件
 * 对应 https://www.highcharts.com.cn/demo/highcharts/spline-symbols
 * 网站api文档
 * 
 * container 表示id
*/
var charts_ops = {
    setOption:function(){
        Highcharts.setOptions({
            chart: {
            },
            exporting: {
                enabled: false
            },
            legend: {
                //enabled:false
            },
            credits:{
                enabled:false
            },
            colors:['#FBDF04','#D81E06','#058DC7', '#50B432', '#ED561B', '#DDDF00',
                '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4','#E93EFF'],
            title: '',
            xAxis: {
                tickWidth:0,
                lineWidth: 0,
                gridLineColor: '#eee',
                //gridLineWidth: 1,
                crosshair: {
                    width: 1,
                    color: '#ebebeb'
                }
            },
            yAxis: {
                gridLineColor: '#eee',
                gridLineWidth: 1,
                title: ''
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    pointWidth: 20,
                    borderWidth: 0
                },
                series: {
                    marker: {
                        enabled: false
                    },
                },
                line: {
                    lineWidth: 2,
                    states: {
                        hover: {
                            lineWidth: 2
                        }
                    }
                }
            },
            tooltip: {
                backgroundColor: '#404750',
                borderWidth: 0,
                shadow: false,
                headerFormat: '',
                footerFormat: '',
                shared: true,
                useHTML: true,
                style: {
                    color: '#fff',
                    padding: '5px'
                }
            },
            lang: {
                noData: "暂无数据"
            },
            noData: {
                style: {
                    fontWeight: 'bold',
                    fontSize: '15px',
                    color: '#303030'
                }
            }
        });
    },
    drawLine:function( target ,data ){//画直线
        var chart =  target.highcharts({
            chart: {
                type: 'spline'
            },
            xAxis: {
                categories: data.categories
            },
            series: data.series,
            legend: {
                enabled:true,
                align: 'right',
                verticalAlign: 'top',
                x: 0,
                y: -15
            }
        });
        return chart;
    }
};




// var chart = Highcharts.chart('container', {
//     chart: {
//         type: 'spline'
//     },
//     title: {
//         text: '两地月平均温度'
//     },
//     subtitle: {
//         text: '数据来源: WorldClimate.com'
//     },
//     xAxis: {
//         categories: ['一月', '二月', '三月', '四月', '五月', '六月',
//                      '七月', '八月', '九月', '十月', '十一月', '十二月']
//     },
//     yAxis: {
//         title: {
//             text: '温度'
//         },
//         labels: {
//             formatter: function () {
//                 return this.value + '°';
//             }
//         }
//     },
//     tooltip: {
//         crosshairs: true,
//         shared: true
//     },
//     plotOptions: {
//         spline: {
//             marker: {
//                 radius: 4,
//                 lineColor: '#666666',
//                 lineWidth: 1
//             }
//         }
//     },
//     series: [
//         {
//         name: '东京',
//         data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
//         }, {
//         name: '伦敦',
//         marker: {
//             symbol: 'diamond'
//         },
//         data: [{
//             y: 3.9,
//             marker: {
//                 symbol: 'url(https://www.highcharts.com/demo/gfx/snow.png)'
//             }
//         }, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
//     }]
// });
