import os
import yagmail
import datetime
import codecs
import requests
import schedule
import time
import pytz
from pyquery import PyQuery as pq
from zhipuai import ZhipuAI


def get_emails(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

def get_ai_analysis(path):
    client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY"))
    def get_trends(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    trends = get_trends(path)
    # print(trends)

    response = client.chat.completions.create(
        model="glm-4-flash",  # 填写需要调用的模型编码
        messages=[
            {"role": "system", "content": "你是一个 github trends 分析专家。负责分析 github 每日 python 项目的趋势。将英文介绍翻译成中文。输出整齐精致。接着在下一行，安利一个最惊艳的项目。再换一行，最后总结今天的趋势项目关注的领域和特点。语言保持简洁。"},
            {"role": "user", "content":f'{trends}' }
        ],
    )

    ans = response.choices[0].message.content
    # print(ans)
    return ans

def createtext(date, filename):
    with open(filename, 'w') as f:
        f.write(date + "\n")

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
        f.write('\n{language}\n'.format(language=language))

        for index, item in enumerate(items, start=1):
            i = pq(item)
            title = i(".lh-condensed a").text()
            owner = i(".lh-condensed span.text-normal").text()
            description = i("p.col-9").text()
            url = i(".lh-condensed a").attr("href")
            url = "https://github.com" + url
            # ownerImg = i("p.repo-list-meta a img").attr("src")
            # print(ownerImg)
            f.write(u"{index}. [{title}]:{description}({url})\n".format(index=index, title=title, description=description, url=url))

def job():
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f'{strdate}.txt'
    createtext(strdate, filename)
    attempts = 0

    while attempts < 3:
        try:
            scrape('python', filename)
            ans = get_ai_analysis(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(ans)
            return filename
        except Exception as e:
            attempts += 1
            print(f"Attempt {attempts} failed with error: {e}")
            time.sleep(300)  # Wait 5min before retrying
    raise Exception("All attempts to scrape data have failed.")

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
    try:
        path = job()
        src = '19121220286@163.com'
        tos = get_emails('emails.txt') #['pxxhl@qq.com']
        subject = '每日 GitHub 趋势项目'
        contents = get_contents(path)
        attachments = path
        
        send_emails(src, tos, subject, contents, attachments)
    except Exception as e:
        print(f"{e} occured in daily_task")

if __name__ == '__main__':
    try:
        # 设置时区为北京时间
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.datetime.now(beijing_tz)

        # 每天定时执行任务
        schedule.every().day.at("18:00", beijing_tz).do(daily_task)

        while True:
            schedule.run_pending()
            time.sleep(1)
        # daily_task()
    except Exception as e:
        print(f"{e} occured~")
