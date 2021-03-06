const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return [year, month, day].map(formatNumber).join('/') + ' ' + [hour, minute, second].map(formatNumber).join(':')
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : '0' + n
}

/*参考文章：https://segmentfault.com/q/1010000008005954/a-1020000008187652*/
/*获取当前页url*/
function getCurrentPageUrl() {
  var pages = getCurrentPages()    //获取加载的页面
  var currentPage = pages[pages.length - 1]    //获取当前页面的对象
  var url = currentPage.route      //当前页面url
  return url
}

/*获取当前页带参数的url  完整的URL*/
function getCurrentPageUrlWithArgs() {
  var pages = getCurrentPages()    //获取加载的页面
  var currentPage = pages[pages.length - 1]    //获取当前页面的对象
  var url = currentPage.route    //当前页面url
  var options = currentPage.options    //如果要获取url中所带的参数可以查看options

  //拼接url的参数
  var urlWithArgs = url + '?'
  for (var key in options) {
      var value = options[key]
      urlWithArgs += key + '=' + value + '&'
  }
  urlWithArgs = urlWithArgs.substring(0, urlWithArgs.length - 1)

  return urlWithArgs
}

// 购物车动画新增
const inArray = (array, value) => {
  for (var i = 0; i < array.length; i++) {
    if (array[i] == element) {
      return i;
    }
  } return -1;
}

function getLocalTime(now) {
  var now = new Date(parseInt(now));
  var year = now.getFullYear();
  var month = now.getMonth() + 1;
  var date = now.getDate();
  var hour = now.getHours();
  var minute = now.getMinutes();
  var second = now.getSeconds();
  return year + "-" + month + "-" + date + " " + hour + ":" + minute //+ ":" + second; 
}

module.exports = {
  formatTime: formatTime,
  getCurrentPageUrl: getCurrentPageUrl,
  getCurrentPageUrlWithArgs: getCurrentPageUrlWithArgs,
  inArray: inArray,
  getLocalTime: getLocalTime
}
