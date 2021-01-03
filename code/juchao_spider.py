"""
从巨潮网上下载所有A股的相关介绍
"""
import requests
import pandas as pd
from collections import OrderedDict
import csv
import time, base64
import random


code_name = OrderedDict({"SECCODE":"证券代码",
                         "SECNAME":"证券简称",
                         "ORGNAME":"机构名称",
                         "F001V":"证券类别",
                         "F002D":"上市日期",
                         "F003V":"上市地点",
                         "F004V":"正常上市",
                         "F005D":"摘牌日期",
                         "F006V":"ISIN代码",
                         "F007V":"英文名称",
                         "F008V":"英文简称",
                         "F009D":"成立日期",
                         "F010N":"注册资本",
                         "F011V":"法定代表人",
                         "F012V":"主营业务",
                         "F013V":"经营范围",
                         "F014V":"公司简介",
                         "F015V":"省份",
                         "F016V":"城市",
                         "F017V":"注册地址",
                         "F018V":"办公地址",
                         "F019V":"邮编",
                         "F020V":"公司电话",
                         "F021V":"公司传真",
                         "F022V":"公司电子邮件地址",
                         "F023V":"公司网站",
                         "F024V":"证监会一级行业名称",
                         "F025V":"证监会二级行业名称",
                         "F026V":"申万行业一级名称",
                         "F027V":"申万行业二级名称",
                         "F028V":"申万行业三级名称",
                         "F029V":"董事长",
                         "F030V":"独立董事",
                         "F031V":"总经理",
                         "F032V":"董事会秘书",
                         "F033V":"董秘电话",
                         "F034V":"董秘传真",
                         "F035V":"董秘邮箱",
                         "F036V":"证券事务代表",
                         "F037V":"会计师事务所",
                         "F038V":"律师事务所"})

def get_data(scode, now):
    url = "http://webapi.cninfo.com.cn/api/sysapi/p_sysapi1018?scode="+scode
    mcode = base64.b64encode(str(int(now)).encode("utf-8"))
    headers = {"Accept": "application/json, text/javascript, */*; q=0.01",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "Connection": "keep-alive",
               "Content-Length": "0",
               "Cookie": "Hm_lvt_489bd07e99fbfc5f12cbb4145adb0a9b=1607933825; Hm_lpvt_489bd07e99fbfc5f12cbb4145adb0a9b=1607995044",
               "Host": "webapi.cninfo.com.cn",
               "mcode": mcode,
               "Origin": "http://webapi.cninfo.com.cn",
               "Referer": "http://webapi.cninfo.com.cn/",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
               "X-Requested-With": "XMLHttpRequest"}
    r = requests.post(url, headers=headers, data={"scode":scode})
    result = r.json()
    if result["resultcode"] == 200:
        return result["records"][0], True
    else:
        print("Error occured: %s" % result)
        return None, False

filename = "D:\Project\jupyter_project\投资理财\data\A股列表-202011.xlsx"
df = pd.read_excel(filename, sheet_name="深圳证券交易所",converters={'公司代码': str})

num = 0
with open("result.csv", "w", newline="") as csvfile:
    fieldnames = [code_name[key] for key in code_name.keys()]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for scode in df["公司代码"]:
        num += 1
        print("%d 获取%s..." % (num, scode))
        now = time.time()
        result, flag = get_data(scode, now)
        try:
            if flag == True:
                result = OrderedDict({code_name[key]:result[key] for key in code_name.keys()})
                writer.writerow(result)
            else:
                time.sleep(5)
                now = time.time()
                result, flag = get_data(scode, now)
                if flag == True:
                    result = OrderedDict({code_name[key]: result[key] for key in code_name.keys()})
                    writer.writerow(result)
                else:
                    exit(0)
        except:
            print("raise error!")

