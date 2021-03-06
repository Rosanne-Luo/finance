#!/usr/bin/env python
# coding: utf-8

# In[28]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_indicators(stockCode, key):
    """
    从雪球网上获取市值，市盈率等数据
    
    key 的取值：['最高', '今开', '涨停', '成交量', '最低', '昨收', '跌停', '成交额', '量比', '换手', '市盈率(动)',
    '市盈率(TTM)', '委比', '振幅', '市盈率(静)', '市净率', '每股收益', '股息(TTM)', '总股本', '总市值', '每股净资产', 
    '股息率(TTM)', '流通股', '流通值', '52周最高', '52周最低', '货币单位']
    """
    
    if stockCode.startswith("0") or stockCode.startswith("3"):
        url = "https://xueqiu.com/S/SZ" + stockCode
    else:
        url = "https://xueqiu.com/S/SH" + stockCode
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "device_id=24700f9f1986800ab4fcc880530dd0ed; acw_tc=2760820816093203071334825ed4d23a25c85e467a9ab6dd1330d07bb9a8ca; xq_a_token=ad26f3f7a7733dcd164fe15801383e62b6033003; xqat=ad26f3f7a7733dcd164fe15801383e62b6033003; xq_r_token=15b43888685621c645835bfe2d97242dc20b9005; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTYxMTI4MzA4NCwiY3RtIjoxNjA5MzIwMjkxMzMxLCJjaWQiOiJkOWQwbjRBWnVwIn0.IVBo7cpp5Al-T1GVvDMh32LRwpuXh1b9ISxU19MRyLdVcTf7yJrnnqtXWSDJ0XW0dg9chpUNd61Kl_frNWggxQMLrxtDpuybvLVWhLTjejzf2PJymy2yIrhCt6Hno8hQ-OO1v4P_zinYNb9UXiyi_eCPlNEzitkXcDsRyAnXH62dKHt9uRFIbtLyixB-lOxwGnAl8A1ZKQqZY-53v2mBqCdg-XPt-VXjmV-XWflFicYY5mQXFthOT3TVwKquoKDwM3NpF27xqLtw1ZDjXyulkIvZNytt_DWO6qaUsNT_SGmQ8KoNgUAy846i2Wlnb-ZClQ19wZjxVTyLc34bKHu7Zg; u=781609320307138; Hm_lvt_1db88642e346389874251b5a1eded6e3=1609320308; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1609320319",
        "Host": "xueqiu.com",
        "Referer": "https://xueqiu.com/k?q=%E5%8C%97%E6%96%B0%E5%BB%BA%E6%9D%90",
        "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    r = requests.get(url, headers=headers)
    bs = BeautifulSoup(r.text, "html.parser")
    tds = bs.find_all("td")

    for td in tds:
        items = td.text.split('：')
        name = items[0]
        value = items[1]
        if name == key:
            return value
        

def get_dec_ratio(stockCode):
    """
    计算52周内，现在的股价相比最高价降低了多少
    """
    new_price = get_indicators(stockCode, "昨收")
    if new_price is None or new_price == "--":
        return None
    
    high_price = get_indicators(stockCode, "52周最高")
    if high_price is None or high_price == "--":
        return None
    
    dec_ratio = 1- float(new_price) / float(high_price)
    return dec_ratio

def monitor_dec_ratio():
    import pandas as pd
    df = pd.read_csv("configs/monitor_dec_ratio.csv", header=0)
    
    result = []
    i = 0
    for stockCode, stockName in zip(df["证券代码"], df["证券简称"]):
        stockCode = str(stockCode).rjust(6, '0')
        i += 1
        if stockCode != '':
            dec_ratio = get_dec_ratio(stockCode)
            #print("{} {}:{:.2f}".format(stockCode, stockName, dec_ratio))
            if dec_ratio is not None and dec_ratio>0.2:
                result.append("<p>{} {}: {:.2f}</p>".format(stockCode, stockName, dec_ratio))
    return "".join(result), len(result)

if __name__ == "__main__":
    print(monitor_dec_ratio())
   

