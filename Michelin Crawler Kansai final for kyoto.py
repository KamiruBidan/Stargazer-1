# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 01:38:13 2017

@author: liuya
"""

import requests
from bs4 import BeautifulSoup
import re
import sqlite3

conn = sqlite3.connect(r'E:\da\Michelin\MichelinKansai.db')
cursor = conn.cursor()
#创建didi表 第一次创建，之后可以注释掉了
#cursor.execute('CREATE TABLE MichelinKansai(id INTEGER PRIMARY KEY,shopname TEXT, star TEXT, comfort TEXT, cuisine TEXT,reservation TEXT, description TEXT, opening TEXT, close TEXT, price TEXT, address TEXT, tel TEXT);')
#关闭cursor
#cursor.close()
#提交事务
conn.commit()

#抓取信息的函数
def getrestaurantdetails(restauranturl):
    result ={}
    res = requests.get(restauranturl)
    soup = BeautifulSoup(res.text, 'html.parser')
    result['shopname'] = soup.select('.px26')[0].text
    result['star'] = soup.select('.rating')[0].text.strip()
    result['comfort'] = soup.select('.amenity')[0].text.strip()
    result['cuisine'] = soup.select('.category')[0].text
    try: 
        result['reservation'] = soup.select('.reservations')[0].text
    except Exception as e:
        print(e)
    result['description'] = soup.select('.px14')[1].text
    result['opening'] = soup.select('.hours > dd')[0].text
    try: 
        result['close'] = soup.select('.holiday > dd')[0].text
    except Exception as e:
        print(e)
    result['price'] = soup.select('.price > dd')[0].text
    result['address'] = soup.select('.address > dd')[0].text
    result['tel'] = soup.select('.tel > dd')[0].text
    return result

def insertOp(cursor, tableName, fields, vs):
    """
    insert 语句
    """
    if len(fields) != len(vs) or len(fields) == 0:
        return
    sql = "insert into " + tableName + " ("
    for field in fields:
        sql += field + ", "
    sql = sql[:-2]
    sql += ") values ("
    #for field in fields:
    #    sql += "%s, "
    #sql = sql[:-2]
    for v in vs:
        sql += '"' + str(v) + '", '
    sql = sql[:-2]
    sql += ')'
    print (sql)
    cursor.execute(sql)
        
        

for pp in range(1,20):
    city_url_format = 'http://gm.gnavi.co.jp/restaurant/list/kyoto/all_area/all_small_area/all_food/all_star/{}'
    try:
        next_page = 'p' + str(pp)
        all_page = city_url_format.format(next_page)
        print(all_page)
        res_kansai = requests.get(all_page)
        soup_kansai = BeautifulSoup(res_kansai.text, 'html.parser')
        for link in soup_kansai.find_all(href=re.compile("shop")):
            shoplink = link.get('href')
            print(shoplink)
            shop_url_format = 'http://gm.gnavi.co.jp{}'
            shop_url = shop_url_format.format(shoplink)
            print(shop_url)
            try:
                restaurant_details = getrestaurantdetails(shop_url)#这是个字典
                cursor = conn.cursor()
                details = list(restaurant_details.values())
                header = list(restaurant_details.keys())
                shopname_detail = restaurant_details['shopname']
                insertOp(cursor, 'MichelinKansai', header, details)
                cursor.close()
                conn.commit()
                #执行SQL写入
                print(restaurant_details)
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)
        continue
conn.close()
