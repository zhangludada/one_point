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

# 初始页面列表
# 创建数据库
db = pymysql.connect(host="localhost",
                     user="root",
                     password="860625",
                     port=3307,  # 端口
                     database="one_point",
                     charset='utf8mb4')
cursor = db.cursor()


# 下载页面 return html
def download_page(download_url):

    # try:
    #     print(download_url)
    #     html = request.urlopen(download_url).read().decode()
    #     return html
    # except:
    #     return ""

    try:

        headers = {
            "User-Agent":
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
        }

        r = requests.get(url=download_url, headers=headers, allow_redirects=False)
        status=r.status_code
        print(download_url,status,end=' ')
        if status!=200:
            # 利用selenium 无头浏览器获取cookies然后重新requests
            return None
        r.encoding=r.apparent_encoding
        html=r.text
        return html
    except:
        print(download_url,'爬取失败',end=' ')
        return None


# 解析页面,获取host域名的A标签
def jx_page_get_a(html_text):
    global url_list
    if html_text == "":
        return
    # html = tree.HTML(html_text)
    # new_a_list = []
    # for href_item in html.xpath("//a/@href"):
    #     urljoin = parse.urljoin("http://" + host, href_item)
    #     new_a_list.append(urljoin)
    # return new_a_list
    doc=pq(html_text)
    new_page_list=set()
    for a in doc('a').items():
        url=str(a.attr('href'))
        if host in url and url not in url_list:
            url_list.add(url)
            new_page_list.add(url)
    return new_page_list


# 向页面列表添加新页面
def save_page(url,html):
    html = pymysql.escape_string(str(html))
    sql = """INSERT INTO WEB_PAGE(url,html, host, state) VALUES ("{}", "{}", "{}", {})"""
    try:
        cursor.execute(sql.format(url,html,host,2))
        # 提交到数据库执行
        db.commit()
        #print("添加新URL：" + urljoin)
        print('ok')
    except:
        print("mysql erro")


def get_new_url_obj():
    sql = "SELECT id,url,host FROM `web_page` where state = 2 order by create_date limit 1"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            return {'id': row[0], 'url': row[1]}
    except:
        print("Error: unable to fecth data")
    pass

def save_html_to_database(id,html):
    state = 1

    if html == "":
        state = 3
    try:
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """update WEB_PAGE set html = %s , state = %s, update_date = %s where id = %s"""
        # sql = """update WEB_PAGE set html = %s ,  update_date = %s where id = %s"""
        cursor.execute(sql,[html, state, date_time,id])
        # 提交到数据库执行
        db.commit()
        print('页面存入成功')
    except:
        db.rollback()
        print("更新页面数据失败")


if __name__ == '__main__':
    url_list = set()
    new_page_list=set({'https://www.cnblogs.com/'})
    id=0
    while new_page_list:
        tmp=set()
        print("id={} 开始：".format(id),end=' ')
        for url in new_page_list:
            html=download_page(url)
            save_page(url,html)
            page_list=jx_page_get_a(html)
            for url1 in page_list:
                tmp.add(url1)
            new_page_list=tmp
            id+=1
            print('#'*40)
            time.sleep(5)
