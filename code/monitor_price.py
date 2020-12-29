#!/usr/bin/env python
# coding: utf-8

# In[8]:


import requests
import json
import time
import base64
import datetime

def is_weekday():
    """
    判断日期是否为工作日（周一到周五）
    """
    today = datetime.datetime.now().weekday()
    if int(today) in range(1,6):
        return True
    else:
        return False
    
def get_newPrice(stock_code, date_time):
    """
    获取股票最新收盘价
    """
    now = time.time()
    mcode = base64.b64encode(str(int(now)).encode("utf-8"))
    url = "http://webapi.cninfo.com.cn/api/sysapi/p_sysapi1008"
    headers = {"Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "58",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "routeId=.uc1; Hm_lvt_489bd07e99fbfc5f12cbb4145adb0a9b=1607933825,1608168643; SID=e5e6b001-8958-4fe2-8a53-bb5e8efd8bd8; cninfo_user_browse=000002,gssz0000002,%E4%B8%87%20%20%E7%A7%91%EF%BC%A1; Hm_lpvt_489bd07e99fbfc5f12cbb4145adb0a9b=1608516249",
            "Host": "webapi.cninfo.com.cn",
            "mcode": mcode,
            "Origin": "http://webapi.cninfo.com.cn",
            "Referer": "http://webapi.cninfo.com.cn/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
          }
    
    if stock_code.startswith("6"):
        scode = stock_code + "-SHE"
    elif stock_code.startswith("0"):
        scode = stock_code + "-SZE"
    else:
        scode = None
    
    data = {
    "scode": scode,
    "sdate": date_time,
    "edate": date_time,
    "ctype": 0
    }

    r = requests.post(url, headers=headers, data=data)
    result = json.loads(r.text)
    if len(result["records"]) != 0:
        new_price = result["records"][0]
        return new_price["收盘价"]
    else:
        return -1

def monitor_price():
    """
    监控股价总函数
    """
    # 判断是否为工作日，非工作日不用执行
    
    date_time = (datetime.datetime.now() + datetime.timedelta(days=-1)).date().strftime('%Y-%m-%d')
    if is_weekday() == False:
        return ;
    else:
        #date_time = "2020-12-20"
        # 获取需要监控的股票列表
        with open("monitor_price.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        write_flag = False
        messages = ["<h1>最新个股股价</h1>\n"]
        for i in range(len(data["records"])):
            record = data["records"][i]
            stockCode = record["stockCode"]
            stockName = record["stockName"]
            minPrice = float(record["minPrice"])
            maxPrice = float(record["maxPrice"])
            new_Price = float(get_newPrice(stockCode, date_time))
            print("{}: 最低价{}，最高价{}, 最新价{}".format(stockCode, minPrice, maxPrice, new_Price))
            
            if new_Price < 0:
                continue
            elif new_Price >= maxPrice:
                if write_flag == False:
                    write_flag = True
                data["records"][i]["maxPrice"] = new_Price
                message = "<p>{} {} {} 股价创新高: {}</p>".format(date_time, stockCode, stockName, new_Price)
                messages.append(message)
            elif new_Price <= minPrice:
                if write_flag == False:
                    write_flag == True
                data["records"][i]["minPrice"] = minPrice
                message = "<p>{} {} {} 股价创新低: {}</p>".format(date_time, stockCode, stockName, new_Price)
                messages.append(message)
            else:
                pass
            
        if write_flag == True:    
            with open("monitor_price.json", "w", encoding="utf-8") as f:
                json.dump(data, f)
            
    return "".join(messages)

if __name__ == "__main__":
    print("run...")
    monitor_price()

