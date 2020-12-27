import urllib.request as request
import urllib.parse as parse
import lxml.etree as tree
import requests
from pyquery import PyQuery as pq
import pymysql
import datetime
import time

# 域名
host = "www.cnblogs.com"

db = pymysql.connect(host="localhost",
                     user="root",
                     password="860625",
                     port=3307,  # 端口
                     database="one_point",
                     charset='utf8mb4')
cursor = db.cursor()

def save_page(url,html):

    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """INSERT INTO WEB_PAGE(url,html, host, state) VALUES ("{}", "{}", "{}", {})"""
    try:
        cursor.execute(sql.format(url,html,host,2))
        # 提交到数据库执行
        db.commit()
        #print("添加新URL：" + urljoin)
        print('ok')
    except:
        print("erro")


html='666'
save_page(host,html)