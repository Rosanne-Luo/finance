#!/usr/bin/env python
# coding: utf-8
import requests
import datetime
from bs4 import BeautifulSoup
import math
import json
import math
import utils

def get_new_industry_research():
    """
    获取最新的行业研报
    :return:
    """
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "intellpositionL=1152px; qgqp_b_id=137163e79bf2202a79b01d4b72947fd1; st_si=87851564198717; em_hq_fls=js; emshistory=%5B%22%E4%B8%87%E7%A7%91%EF%BC%A1%22%2C%22%E4%B8%AD%E5%9B%BD%E5%B7%A8%E7%9F%B3%22%5D; HAList=a-sh-600176-%u4E2D%u56FD%u5DE8%u77F3%2Ca-sz-000002-%u4E07%20%20%u79D1%uFF21; cowCookie=true; cowminicookie=true; st_asi=delete; st_pvi=60810721189694; st_sp=2020-05-06%2011%3A32%3A35; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=49; st_psi=20201229165404514-113300303753-0542765375; intellpositionT=2791px",
        "Host": "reportapi.eastmoney.com",
        "Referer": "http://data.eastmoney.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    pageSize = 50
    pageNum = 1

    end_time = datetime.datetime.now().strftime('%Y-%m-%d')
    start_time = (datetime.datetime.now() + datetime.timedelta(days=-5)).date().strftime('%Y-%m-%d')
    yesterday = utils.get_yesterday()

    url = ("http://reportapi.eastmoney.com/report/list?"
           "cb=datatable5893892&industryCode=*"
           "&pageSize="+str(pageSize)+"&industry=*&rating=*"
           "&ratingChange=*&beginTime="+start_time+"&endTime="+end_time+
           "&pageNo="+str(pageNum)+"&fields=&qType=1&orgCode=&rcode=&p="+str(pageNum)+"&pageNum="+str(pageNum)+"&_=1609232044235")

    #print(url)
    r = requests.get(url, headers=headers)
    result = r.text
    left_index = result.find("{")
    right_index = result.rfind("}")
    result = result[left_index:right_index+1]
    result = json.loads(result)
    hits = result["hits"]
    pages = math.ceil(hits / pageSize)

    monitor_industry = {"424":"水泥建材",
                        "427":"公用事业",
                        "451":"房地产",
                        "456":"家电行业"}

    messages = []
    num = 0
    for pageNum in range(1, pages+1):
        url = ("http://reportapi.eastmoney.com/report/list?"
           "cb=datatable5893892&industryCode=*"
           "&pageSize="+str(pageSize)+"&industry=*&rating=*"
           "&ratingChange=*&beginTime=+"+start_time+"&endTime="+end_time+
           "&pageNo="+str(pageNum)+"&fields=&qType=1&orgCode=&rcode=&p="+str(pageNum)+"&pageNum="+str(pageNum)+"&_=1609232044235")

        r = requests.get(url, headers=headers)
        result = r.text
        left_index = result.find("{")
        right_index = result.rfind("}")
        result = result[left_index:right_index+1]
        result = json.loads(result)

        datas = result["data"]
        for data in datas:
            title = data["title"]
            orgSName = data["orgSName"]
            publishDate = data["publishDate"][0:10]
            industryCode = data["industryCode"]
            industryName = data["industryName"]
            infoCode = data["infoCode"]
            report = "<p><a href='http://data.eastmoney.com/report/zw_industry.jshtml?infocode={}'>{}-{}-{}-{}</a></p>".format(infoCode, publishDate, industryName, title, orgSName)
            if industryCode in monitor_industry.keys() and title.find("周报")==-1 and publishDate==yesterday:
                messages.append(report)
               #print(report)
                num += 1
    return "".join(messages), num

if __name__ == "__main__":
    get_new_industry_research()

