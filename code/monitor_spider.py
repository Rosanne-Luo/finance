"""
监控A股公告
"""

import requests
from bs4 import BeautifulSoup
import json
import math
import datetime
import configure
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import smtplib
import logging
import utils
import monitor_price
import monitor_industry_research

def get_szse():
    """
    获取深圳证券交易所的公告数据
    :return: messages
    """
    url = "http://www.szse.cn/api/disc/announcement/annList?random=0.6527177005495639"
    pageSize = 30
    pageNum = 1

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "100",
        "Content-Type": "application/json",
        "Host": "www.szse.cn",
        "Origin": "http://www.szse.cn",
        "Referer": "http://www.szse.cn/disclosure/listed/notice/index.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "X-Request-Type": "ajax",
        "X-Requested-With": "XMLHttpRequest"
    }

    date = utils.get_yesterday()
    data = {"seDate":[date,date],"channelCode":["listedNotice_disc"],"pageSize":30,"pageNum":1}
    r = requests.post(url, headers=headers, data=json.dumps(data))

    result = r.json()
    total_num = result["announceCount"]
    page_numbers = math.ceil(total_num / pageSize)

    messages = ""
    num = 0
    for i in range(1, page_numbers+1):
        pageNum = i
    #   print("page number:%d" % pageNum)
        data = {"seDate":[date,date],"channelCode":["listedNotice_disc"],"pageSize":30,"pageNum":pageNum}
        r = requests.post(url, headers=headers, data=json.dumps(data))
        result = r.json()
        for item in result["data"]:
            secCode = item["secCode"][0]
            secName =  item["secName"][0]
            title = item["title"]
            publishTime = item["publishTime"][0:10]
            pdf_url = "http://www.szse.cn/disclosure/listed/bulletinDetail/index.html?" + item["id"]

            if publishTime == date and secCode in configure.MONITOR_STOCKS.keys():
                message = "<p><a href={}>{} {} {} {}</a></p>".format(pdf_url, secCode, secName, title,
                                                                 publishTime)
                messages = messages + message + "\n"
                num += 1
    return messages, num

def get_shanghai():
    url = "http://www.sse.com.cn/disclosure/listedinfo/bulletin/s_docdatesort_desc_2019openpdf_new.htm"
    headers = {
        "Accept": "text/html, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Cookie": "yfx_c_g_u_id_10000042=_ck20121220243710650804792806023; yfx_mr_f_10000042=%3A%3Amarket_type_free_search%3A%3A%3A%3Abaidu%3A%3A%3A%3A%3A%3A%3A%3Awww.baidu.com%3A%3A%3A%3Apmf_from_free_search; yfx_mr_10000042=%3A%3Amarket_type_free_search%3A%3A%3A%3Abaidu%3A%3A%3A%3A%3A%3A%3A%3Awww.baidu.com%3A%3A%3A%3Apmf_from_free_search; yfx_key_10000042=; VISITED_COMPANY_CODE=%5B%22600000%22%2C%22600031%22%2C%22600004%22%5D; VISITED_STOCK_CODE=%5B%22600000%22%2C%22600031%22%2C%22600004%22%5D; seecookie=%5B600000%5D%3A%u6D66%u53D1%u94F6%u884C%2C%5B600031%5D%3A%u4E09%u4E00%u91CD%u5DE5%2C%5B600004%5D%3A%u767D%u4E91%u673A%u573A; sseMenuSpecial=8348; VISITED_MENU=%5B%229063%22%2C%229061%22%2C%228454%22%2C%228464%22%2C%2211913%22%2C%228528%22%2C%229055%22%2C%229062%22%2C%228535%22%2C%228536%22%2C%228349%22%5D; yfx_f_l_v_t_10000042=f_t_1607775877050__r_t_1608350541120__v_t_1608354745748__r_c_2",
        "Host": "www.sse.com.cn",
        "Origin": "http://www.sse.com.cn",
        "Referer": "http://www.sse.com.cn/disclosure/listedinfo/announcement/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    r = requests.post(url, headers=headers)
    r.encoding='utf-8'

    bs = BeautifulSoup(r.text, "html.parser")
    tables = bs.find_all("tr")

    date = utils.get_yesterday()
    messages = ""
    num = 0
    for i in range(1, len(tables)):
        tds = tables[i].find_all("td")
        secCode = tds[0].text
        secName = tds[1].text.strip()
        title = tds[2].text.strip()
        href = tds[2].a.attrs["href"]
        publishTime = tds[2].attrs["data-time"].strip()
        if publishTime == date and secCode in configure.MONITOR_STOCKS.keys():
            message = "<p><a href={}>{} {} {} {}</a></p>".format(href, secCode, secName, title,
                                                                 publishTime)
            messages = messages + message + "\n"
            num += 1

    return messages, num


def get_yanbao_dongfangcaifu():
    """
    从东方财富上监控个股研报
    :return:
    """
    url = "http://data.eastmoney.com/report/stock.jshtml?hyid=BK0546"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "cowCookie=true; intellpositionL=1152px; qgqp_b_id=137163e79bf2202a79b01d4b72947fd1; st_si=87851564198717; st_pvi=60810721189694; st_sp=2020-05-06%2011%3A32%3A35; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=3; st_psi=20201217171702172-113300303752-5081476687; cowminicookie=true; st_asi=20201217171702172-113300303752-5081476687-dfcfwsy_dfcfwxsy_dcxn_djgb-1; intellpositionT=938px",
        "Host": "data.eastmoney.com",
        "Referer": "http://data.eastmoney.com/report/singlestock.jshtml?stockcode=600176&market=SHANGHAI",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    r = requests.get(url, headers=headers)
    bs = BeautifulSoup(r.text, "html.parser")

    scripts = bs.find_all("script")
    result = scripts[8].contents
    result = result[0]

    left_index = result.find("{")
    right_index = result.rfind("}")
    result = result[left_index:right_index + 1]
    result = json.loads(result)

    date = utils.get_yesterday()

    messages = ""
    num = 0
    for item in result["data"]:
        url = "http://data.eastmoney.com/report/zw_stock.jshtml?infocode=" + item["infoCode"]
        publishDate = item["publishDate"][0:10]
        if publishDate == date and item["stockCode"] in configure.MONITOR_STOCKS.keys():
            message = "<p><a href={}>{} {} {} {}</a></p>".format(url, item["stockCode"], item["stockName"],
                                                                 item["title"],
                                                                 item["publishDate"][0:10])
            messages = messages + message + "\n"
            num += 1
        else:
            continue

    return messages, num

def sendEmail(messages):
    """
    发送邮件
    :param messages:
    :return:
    """
    try:
        content = MIMEText(messages, 'html',
                           'utf-8')  # 第一个参数：邮件的内容；第二个参数：邮件内容的格式，普通的文本，可以使用:plain,如果想使内容美观，可以使用:html；第三个参数：设置内容的编码，这里设置为:utf-8
        reveivers = configure.RECEIVER_EMAIL
        content['To'] = reveivers  # 设置邮件的接收者，多个接收者之间用逗号隔开
        content['From'] = configure.SEND_EMAIL  # 邮件的发送者,最好写成str("这里填发送者")，不然可能会出现乱码
        content['Subject'] = "财务日报"  # 邮件的主题

        ##############使用qq邮箱的时候，记得要去开启你的qq邮箱的smtp服务；##############
        # 方法：
        # 1）登录到你的qq邮箱；
        # 2）找到首页顶部的【设置】并点击；
        # 3）找到【账户】这个选项卡并点击，然后在页面中找到“SMTP”相关字样，找到【开启】的超链接，点击后会告诉你开启方法（需要发个短信），然后按照指示操作，最终会给你一个密码，这个密码可以用于在代码中当作邮箱密码
        # 注意!!!:163邮箱之类的不知道要不要这些操作，如果是163邮箱你可以忽略此步骤
        ###########################################################################
        smtp_server = smtplib.SMTP_SSL("smtp.qq.com",
                                       465)  # 第一个参数：smtp服务地址（你发送邮件所使用的邮箱的smtp地址，在网上可以查到，比如qq邮箱为smtp.qq.com） 第二个参数：对应smtp服务地址的端口号
        smtp_server.login(configure.SMTP_SERVER_USER, configure.SMTP_SERVER_PASS)  # 第一个参数：发送者的邮箱账号 第二个参数：授权码
        #################################

        smtp_server.sendmail(configure.SEND_EMAIL, [configure.RECEIVER_EMAIL],
                             content.as_string())  # 第一个参数：发送者的邮箱账号；第二个参数是个列表类型，每个元素为一个接收者；第三个参数：邮件内容
        smtp_server.quit()  # 发送完成后加上这个函数调用，类似于open文件后要跟一个close文件一样
    except Exception as e:
        print(str(e))


logging.basicConfig(level=logging.INFO, filename='logs\output.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("开始获取信息...")
messages = "<h1>最新个股公告</h1>\n"
result, num1 =  get_shanghai()
logger.info("上海证券交易所有{}条公布的公告".format(num1))
messages += result
result, num2 =  get_szse()
messages += result
logger.info("深圳证券交易所有{}条公布的公告".format(num2))

messages += "<h1>最新个股研报</h1>\n"
result, num3 = get_yanbao_dongfangcaifu()
messages += result
logger.info("A股共有{}个发布的研报".format(num3))

messages += "<h1>最新股价监控</h1>"
result, num4 = monitor_price.monitor_price()
messages += result
logger.info("共有{}个股价创新高/新低".format(num4))

messages += "<h1>最新行业研报</h1>"
result, num5 = monitor_industry_research.get_new_industry_research()
messages += result
logger.info("共有{}个行业研报".format(num5))

if num1 or num2 or num3 or num4 or num5:
    #print(messages)
    sendEmail(messages)
    logger.info("邮件发送成功!")
else:
    logger.info("没有更新的数据!")