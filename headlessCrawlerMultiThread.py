import json
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import threading
import queue

# 使用插件chrimedriver.exe
options = webdriver.ChromeOptions()
# options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('blink-settings=imagesEnabled=false')
# options.add_argument('--headless')

# config
filename = "output.txt"
content_timeout = 5
release_time_timeout = 10
start_pn = 8700


def dynamic_crawlTieba():
    base_url = "https://tieba.baidu.com/f?kw=%E9%BE%99%E5%8D%8E&ie=utf-8"
    browser = webdriver.Chrome(executable_path=r'/Users/apple/utils/chromedriver', options=options)
    task_q = queue.Queue()
    res_q = queue.Queue()
    threads = []
    for i in range(2):
        t = threading.Thread(target=worker, args=(task_q, res_q))
        t.start()
        threads.append(t)

    # init
    pn_num = start_pn

    # for pn in range 100000:
    while pn_num <= 100000:
        url = base_url + '&pn=' + str(pn_num)
        browser.get(url)
        WebDriverWait(browser, timeout=3).until(
            lambda d: d.find_element(By.XPATH, r'/html/body/div[3]/div/div[2]/div/div/div[1]/div/div/div/div[4]/ul/li'))
        item_list = browser.find_elements(By.XPATH,
                                          r'/html/body/div[3]/div/div[2]/div/div/div[1]/div/div/div/div[4]/ul/li')
        record_num = 0
        # crawl title and link
        for item in item_list:
            try:
                record = Record()
                title = item.find_element(By.TAG_NAME, 'a')
                record.title = title.get_attribute('innerText')
                record.link = title.get_attribute('href')

                rep_num_ele = item.find_element(By.TAG_NAME, 'span')
                rep_num_text = rep_num_ele.get_attribute('innerText')
                if len(rep_num_text) > 0:
                    record.rep_num = int(rep_num_text)
                if record.rep_num >= 10 and len(record.link) > 20:
                    task_q.put(record)
                    record_num = record_num + 1
            except:
                continue

        # wait for workers
        while res_q.qsize() < record_num:
            sleep(1)
            # TODO: may be timeout

        # write file
        with open(filename, 'a') as f:
            while res_q.qsize() > 0:
                record = res_q.get(block=True)
                f.writelines(json.dumps(record.__dict__, ensure_ascii=False))
                f.write(",\n")
                res_q.task_done()
        # while body
        print("pn=" + str(pn_num) + " finished")
        pn_num += 50

    # quit crawling
    task_q.join()
    res_q.join()
    for t in threads:
        t.join()
    browser.quit()

def worker(task_q, res_q):
    browser = webdriver.Chrome(executable_path=r'/Users/apple/utils/chromedriver', options=options)
    while True:
        try:
            record = task_q.get(block=True)
            browser.get(record.link)
            WebDriverWait(browser, timeout=content_timeout).until(
                lambda d: d.find_element(By.XPATH, r'//*[@class="d_post_content j_d_post_content  clearfix"]'))
            record.content = browser.find_element(By.XPATH,
                                                  '//*[@class="d_post_content j_d_post_content  clearfix"]').get_attribute(
                'innerText')
            record.content = record.content.replace('\n', '').replace('\r', '')
            res_q.put(record)
            task_q.task_done()
        except:
            break
    browser.quit()


class Record:
    title = ''
    time = ''
    content = ''
    rep_num = 0
    link = ''

def getSecondLevel(url):
    browser = webdriver.Chrome(executable_path=r'/Users/apple/utils/chromedriver_mac64/chromedriver', options=options)
    browser.get(url)
    WebDriverWait(browser, timeout=content_timeout).until(
        lambda d: d.find_element(By.XPATH, r'//*[@class="d_post_content j_d_post_content  clearfix"]'))
    content = browser.find_element(By.XPATH,
                                          '//*[@class="d_post_content j_d_post_content  clearfix"]').get_attribute(
        'innerText')
    content = content.replace('\n', '').replace('\r', '').strip()
    # get time
    release_time = browser.find_element(By.CLASS_NAME, "l_post j_l_post l_post_bright")
    release_time = release_time.get_attribute('data-field')
    release_time = json.loads(release_time)
    time = release_time["content"]["date"]
    print(time)
    browser.quit()


# deprecated
def getPage(base_url, browser):
    browser.get(base_url)
    WebDriverWait(browser, timeout=3).until(lambda d: d.find_element(By.XPATH, r'/html/body/div[3]/div/div[2]/div/div/div[1]/div/div/div/div[4]/ul/li'))
    item_list = browser.find_elements(By.XPATH, r'/html/body/div[3]/div/div[2]/div/div/div[1]/div/div/div/div[4]/ul/li')
    record_list = []
    # crawl title and link

    for item in item_list:
        try:
            record = Record()
            title = item.find_element(By.TAG_NAME, 'a')
            record.title = title.get_attribute('innerText')
            record.link = title.get_attribute('href')

            rep_num_ele = item.find_element(By.TAG_NAME, 'span')
            rep_num_text = rep_num_ele.get_attribute('innerText')
            if len(rep_num_text) > 0:
                record.rep_num = int(rep_num_text)
            if record.rep_num >= 10 and len(record.link) > 20:
                record_list.append(record)
        except:
            continue

    # crawl content and time
    for record in record_list:
        try:
            browser.get(record.link)
            WebDriverWait(browser, timeout=content_timeout).until(
                lambda d: d.find_element(By.XPATH, r'//*[@class="d_post_content j_d_post_content  clearfix"]'))
            record.content = browser.find_element(By.XPATH, '//*[@class="d_post_content j_d_post_content  clearfix"]').get_attribute('innerText')
            record.content = record.content.replace('\n', '').replace('\r', '').strip()
            # scroll to time
            # target = browser.find_element(By.XPATH, r'//*[@id="j_p_postlist"]/div[2]')
            # browser.execute_script("arguments[0].scrollIntoView();", target)  # 拖动到二楼
            # browser.execute_script("window.scrollBy(0, -500)")  # 往回拖一点
            # WebDriverWait(browser, timeout=release_time_timeout).until(
            #     lambda d: d.find_element(By.XPATH, r'//*[@id="j_p_postlist"]/div[1]/div[3]/div[3]/div[2]/ul[2]/li[2]/span'))
            # record.time = browser.find_element(By.XPATH, '//*[@id="j_p_postlist"]/div[1]/div[3]/div[3]/div[2]/ul[2]/li[2]/span').get_attribute('innerText')
        except:
            # print("timeout:", record.title)
            continue

    # wirte file
    with open(filename, 'a') as f:
        for record in record_list:
            # print(json.dumps(record.__dict__, ensure_ascii=False))
            f.writelines(json.dumps(record.__dict__, ensure_ascii=False))
            f.write(",\n")