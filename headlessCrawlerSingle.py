from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import json
import time

# chrome driver config
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('blink-settings=imagesEnabled=false')

# project config
base_url = "https://tieba.baidu.com/f?kw=%E9%BE%99%E5%8D%8E&ie=utf-8"
min_rep_num = 10
Timeout = 3
filename = "output.txt"
start_pn = 0
stop_pn = 100000

def dynamic_crawling():
    browser = webdriver.Chrome(chrome_options=chrome_options)
    pn = start_pn

    while pn <= stop_pn:
        url = base_url + '&pn=' + str(pn)
        browser.get(url)
        WebDriverWait(browser, timeout=Timeout).until(
            lambda d: d.find_element(By.XPATH, r'/html/body/div[3]/div/div[2]/div/div/div[1]/div/div/div/div[4]/ul/li'))
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
                if record.rep_num >= min_rep_num and len(record.link) > 20:
                    record_list.append(record)
            except:
                continue

        # crawl secondlevel
        for record in record_list:
            try:
                browser.get(record.link)
                WebDriverWait(browser, timeout=Timeout).until(
                    lambda d: d.find_element(By.XPATH, r'//*[@class="d_post_content j_d_post_content  clearfix"]'))
                record.content = browser.find_element(By.XPATH,
                                                      '//*[@class="d_post_content j_d_post_content  clearfix"]').get_attribute(
                    'innerText')
                record.content = record.content.replace('\n', '').replace('\r', '').strip()
                # crawl time
                release_time = browser.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/div/div[4]/div[1]/div[3]/div[1]').get_attribute('data-field')
                release_time = json.loads(release_time)
                record.time = release_time["content"]["date"]
            except:
                print("timeout:", record.title, record.link)
                continue

        #wirte file
        with open(filename, 'a', encoding='utf8') as f:
            for record in record_list:
                f.writelines(json.dumps(record.__dict__, ensure_ascii=False))
                f.write(",\n")

        # while body
        print("pn=" + str(pn) + " finished " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        pn += 50



class Record:
    title = ''
    time = ''
    content = ''
    rep_num = 0
    link = ''