import urllib.request as request
import urllib.parse as parse
import lxml.etree as tree
import pymysql
import datetime
import time

# 域名
host = "www.cnblogs.com"
# 初始页面列表
# 创建数据库
db = pymysql.connect(host="localhost",
                     user="root",
                     password="mima123456..",
                     port=3306,  # 端口
                     database="my_data",
                     charset='utf8mb4')
cursor = db.cursor()


# 下载页面
def download_page(download_url):
    try:
        print(download_url)
        html = request.urlopen(download_url).read().decode()
        return html
    except:
        return ""


# 解析页面,获取host域名的A标签
def jx_page_get_a(html_text):
    if html_text == "":
        return
    html = tree.HTML(html_text)
    new_a_list = []
    for href_item in html.xpath("//a/@href"):
        urljoin = parse.urljoin("http://" + host, href_item)
        new_a_list.append(urljoin)
    return new_a_list


# 向页面列表添加新页面
def add_new_page_url(a_url_list):
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in a_url_list:
        urljoin = parse.urljoin("http://" + host, item)
        if parse.urlparse(urljoin).netloc == host:
            sql = """INSERT INTO WEB_PAGE(url, host, state, update_date, create_date) VALUES (%s, %s, %s, %s, %s)"""
            try:
                cursor.execute(sql,[urljoin,host,2,date_time,date_time])
                # 提交到数据库执行
                db.commit()
                #print("添加新URL：" + urljoin)
            except:
                # 发生错误时回滚
                #print("添加新URL导入数据库异常：" + urljoin)
                db.rollback()


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


def save_html_to_database(id, html):
    state = 1

    if html == "":
        state = 3
    try:
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """update WEB_PAGE set html = %s , state = %s, update_date = %s where id = %s"""
        cursor.execute(sql,[html, state, date_time,id])
        # 提交到数据库执行
        db.commit()
    except:
        db.rollback()
        print("更新页面数据失败")


if __name__ == '__main__':
    add_new_page_url(["https://www.cnblogs.com/"])
    while True:
        url = get_new_url_obj()
        time.sleep(2)
        page = download_page(url["url"])
        save_html_to_database(url["id"], page)
        a_href_list = jx_page_get_a(page)
        if a_href_list == None:
            continue
        add_new_page_url(a_href_list)

