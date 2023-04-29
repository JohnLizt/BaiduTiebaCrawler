import requests
from bs4 import BeautifulSoup
import os
import json
import time
from time import sleep

# config
start_pn = 400
filename = "output1.txt"
base_url = "https://tieba.baidu.com/f?kw=%E9%BE%99%E5%8D%8E&ie=utf-8"
min_rep_num = 10


headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Host": "httpbin.org",
    "Referer": "https://link.zhihu.com/?target=https%3A//httpbin.org/headers",
    "Sec-Ch-Ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"macOS\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "X-Amzn-Trace-Id": "Root=1-644a6c3d-4e6572f374e23883221f336b"
}


def crawlTieba():
    pn_num = start_pn
    while pn_num <= 100000:
        url = base_url + '&pn=' + str(pn_num)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "lxml")
        item_list = soup.find_all("li", class_="j_thread_list clearfix thread_item_box")
        # blocked
        if len(item_list) == 0:
            print("blocked " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            break

        record_list = []

        for item in item_list:
            record = Record()
            try:
                record.title = item.find("a", class_="j_th_tit").string
                record.link = "https://tieba.baidu.com" + item.find("a", class_="j_th_tit")['href']
                record.rep_num = int(item.find("span", class_="threadlist_rep_num center_text").string)
                # filter rep_num
                if record.rep_num >= min_rep_num and len(record.link) > 20:
                    res_second_level = requests.get(record.link)
                    soup_second_level = BeautifulSoup(res_second_level.content, "lxml")
                    content = soup_second_level.find("div", class_="d_post_content j_d_post_content clearfix").text
                    if content is not None and len(content) > 0:
                        record.content = content.replace('\n', '').replace('\r', '').strip()
                    release_time = soup_second_level.find("div", class_="l_post j_l_post l_post_bright")['data-field']
                    release_time = json.loads(release_time)
                    record.time = release_time["content"]["date"]
                    record_list.append(record)
                    sleep(1)
            except:
                print("crawl error:" + record.title)
                continue

        # wirte file
        with open(filename, 'a') as f:
            for record in record_list:
                # print(json.dumps(record.__dict__, ensure_ascii=False))
                f.writelines(json.dumps(record.__dict__, ensure_ascii=False))
                f.write(",\n")
        print("pn=" + str(pn_num) + " finished " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        pn_num = pn_num + 50



class Record:
    title = ''
    time = ''
    content = ''
    rep_num = 0
    link = ''