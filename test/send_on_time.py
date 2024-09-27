import os
import yagmail
import datetime
import codecs
import requests
import schedule
import time
import pytz
from pyquery import PyQuery as pq

def createMarkdown(date, filename):
    with open(filename, 'w') as f:
        f.write("## " + date + "\n")

def scrape(language, filename):
    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/trending/{language}'.format(language=language)
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200
    
    d = pq(r.content)
    items = d('div.Box article.Box-row')

    # codecs to solve the problem utf-8 codec like chinese
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n### {language}\n'.format(language=language))

        for item in items:
            i = pq(item)
            title = i(".lh-condensed a").text()
            owner = i(".lh-condensed span.text-normal").text()
            description = i("p.col-9").text()
            url = i(".lh-condensed a").attr("href")
            url = "https://github.com" + url
            # ownerImg = i("p.repo-list-meta a img").attr("src")
            # print(ownerImg)
            f.write(u"* [{title}]({url}):{description}\n".format(title=title, url=url, description=description))

def job():
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = '{date}.md'.format(date=strdate)

    # create markdown file
    createMarkdown(strdate, filename)

    # write markdown
    scrape('python', filename)

    return filename

def get_contents(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def send_email(src, dst, subject, contents, attachments):
    pwd = os.environ.get('wangyi_emai_auth')

    yag = yagmail.SMTP(user=src, password=pwd, host='smtp.163.com', port='465')
    yag.send(to=dst, subject=subject, contents=contents, attachments=attachments)
    yag.close()

def send_emails(src, tos, subject, contents, attachments):
    for to in tos:
        send_email(src, to, subject, contents, attachments)  

def daily_task():
    path = job()
    src = '19121220286@163.com'
    tos = ['pxxhl@qq.com']
    subject = '每日 GitHub 趋势项目'
    contents =get_contents(path)
    attachments = path
    
    send_emails(src, tos, subject, contents, attachments)

if __name__ == '__main__':
    # # 设置时区为北京时间
    # beijing_tz = pytz.timezone('Asia/Shanghai')
    # now = datetime.datetime.now(beijing_tz)

    # # 每天12:30执行任务
    # schedule.every().day.at("12:12", beijing_tz).do(daily_task)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    daily_task()