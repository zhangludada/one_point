import urllib.request as request
import urllib.parse as parse
import lxml.etree as tree
import requests
from pyquery import PyQuery as pq
import pymysql
import datetime
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from requests.cookies import RequestsCookieJar

# 创建表
# sql = "create table WEB_PAGE ( id int(32) primary key  auto_increment, url text, html longtext, host varchar(32), state int(32), create_date datetime  DEFAULT NOW() not NULL, update_date datetime  DEFAULT NOW() not NULL );"


# 域名
host = "www.cnblogs.com"
state=2

# 初始页面列表
# 创建数据库
db = pymysql.connect(host="127.0.0.1",
                     user="root",
                     password="860625",
                     port=3307,  # 端口
                     database="one_point",
                     charset='utf8mb4')
cursor = db.cursor()

#保存cookies
def save_cookies(url):
    option=webdriver.FirefoxOptions()
    option.headless=True
    option.add_argument('--disable-gpu')
    # option.add_argument('-headless')

    b=webdriver.Firefox(firefox_options=option)
    b.get(url)
    WebDriverWait(b,20).until(EC.presence_of_all_elements_located)
    cookies=b.get_cookies()
    b.close()
    with open('cookies.json',mode='w',encoding='utf-8') as f:
        json.dump(cookies,f,ensure_ascii=False)

def req(url):
    headers = {
        "User-Agent":
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    with open('cookies.json', mode='r', encoding='utf-8') as f:
        cookies = json.load(f)

    with requests.Session() as s:
        jar = RequestsCookieJar()
        for cookie in cookies:
            jar.set(cookie['name'], cookie['value'])
        s.headers = headers
        r = s.get(url, allow_redirects=False)
        r.encoding = r.apparent_encoding
        status = r.status_code
        return status,r.text

# 下载页面 return html
def download_page(download_url):

    # try:
    #     print(download_url)
    #     html = request.urlopen(download_url).read().decode()
    #     return html
    # except:
    #     return ""
    global count ,state
    count+=1
    print("count={},start:".format(count),end=' ')
    try:
        html='666' #申明变量
        for i in range(4):
            status,html=req(url)
            if status!=200:
                state=2
                save_cookies(url)
            else:
                state=1
                return html
        return html
    except:
        print(download_url,'爬取失败',end=' ')
        return ''


# 解析页面,获取host域名的A标签
def jx_page_get_a(html_text):
    global url_list
    if html_text == "":
        return

    doc=pq(html_text)
    new_page_list=set()
    for a in doc('a').items():
        url=str(a.attr('href'))
        if host in url and url not in url_list:
            url_list.add(url)
            new_page_list.add(url)
    return new_page_list

# 向页面列表添加新页面
def save_page_mysql(url,html):
    global host,state
    host= pymysql.escape_string(host)
    url = pymysql.escape_string(url)
    html = pymysql.escape_string(html)
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """INSERT INTO WEB_PAGE(url,html, host, state) VALUES ("{}", "{}", "{}", {})"""

    try:
        cursor.execute(sql.format(url,html,host,state,date_time,date_time))
        # 提交到数据库执行
        db.commit()
        #print("添加新URL：" + urljoin)
        print('mysql ok')
    except:
        print("mysql erro")

# url是否在数据库内
def is_in_mysql(url):
    url=pymysql.escape_string(url)
    cmd = """
        select state from WEB_PAGE where url="{}"
        """.format(url)
    cursor.execute(cmd)
    res=cursor.fetchall()
    if len(res)==0:
        print("url 不在数据库内")
        return False
    else:
        print("url 在数据库内")
        return True

if __name__ == '__main__':
    #初始化
    count=0
    url_list = set()
    new_page_list=set({'https://www.cnblogs.com/'})
    save_cookies('https://www.cnblogs.com/')

    while new_page_list:
        tmp=set()
        for url in new_page_list:
            # url不在数据库内
            if not is_in_mysql(url):
                html=download_page(url) #获取页面
                save_page_mysql(url,html) #保存页面
                # 分隔符 & 等待
                print('#' * 80)
                time.sleep(5)
                page_list=jx_page_get_a(html) #获取页面中的本域名url
                if page_list:
                    for url1 in page_list:
                        tmp.add(url1)
        new_page_list=tmp

