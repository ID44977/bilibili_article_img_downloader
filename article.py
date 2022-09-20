import os
import re
import time
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image

chromedriver = r".\chromedriver.exe"
chrome = Chrome(executable_path=chromedriver)

IMG_PATH = r".\img\\"
UID = '23155887'
TIME_SLEEP = 1


def scroll(driver):
    """
    根据页面高度设置滚动
    :param driver: selenium chrome driver
    :return:
    """

    i = 0
    scroll_sum = 1000
    driver.execute_script(f'var q=document.documentElement.scrollTop={scroll_sum}')
    time.sleep(TIME_SLEEP)
    height = driver.execute_script('let h = document.body.scrollHeight; return h;')
    # print(height)
    j = int(height / 1000) + 2
    while i < j:
        driver.execute_script(f'var q=document.documentElement.scrollTop={scroll_sum}')
        time.sleep(TIME_SLEEP)
        i += 1
        scroll_sum += 1000
        # print(scroll_sum)
        if scroll_sum > height:
            break
    return True


# def start(article_nums):
#     chrome.execute_script('var q=document.documentElement.scrollTop=3500')
#     time.sleep(5)
#     items = chrome.find_elements(By.CSS_SELECTOR, '.article-item')
#     for item in items:
#         a.append(item.find_element(By.CSS_SELECTOR, '.article-title  a').get_attribute('href'))
#     print(len(a))
#     if len(a) < article_nums:
#         try:
#             chrome.find_element(By.CLASS_NAME, 'be-pager-next').click()
#         except:
#             print("未找到按钮或已到最后一页")
#         time.sleep(3)
#         print("参数：" + str(article_nums - len(items)))
#         start(article_nums - len(items))
#     else:
#         get_img(a)


def find_cv_number(_cv_list, _uid):  # 根据uid查找cv号
    """
    from https://github.com/TK-DS-DS/Crawler-BiliBili
    :param _cv_list: 专栏cv号list
    :param _uid: up主的uid
    :return: 专栏cv号list
    """

    page = 1  # 预定义page，即从第1页开始查找
    while 1:
        localurl = 'https://api.bilibili.com/x/space/article?mid=' + _uid + '&pn=' + str(page)  # 合成具有cv号信息的网页A
        res = requests.get(url=localurl)  # 请求A
        html = res.text  # 转换A为文本
        length = len(res.content)  # 计算A的文本的长度
        if length < 100:  # 小于100算作无新的cv号了
            break
        # print('len=' + str(length))    #输出A的文本的长度
        rst = re.findall('{"id":(.*?),".*?":{".*?,".*?",".*?"', html)  # 更具正则表达式提取具有cv号的文本
        # list.append(re.findall('[0-9]{7}', str(rst)))   #提取cv号 0后面继续添加
        # rstforprint = re.findall('[0-9]{7}', str(rst))  #用于打印的cv号列表
        print('page=' + str(page))  # 打印这是第几页
        # print(rstforprint,"No use")  #打印cv号列表
        print(len(rst))

        # 每个cv号，调用cv下载img函数
        for i in range(len(rst)):
            full_cv_url = 'https://www.bilibili.com/read/cv' + str(rst[i])
            # print(full_cv_url)
            while get_img(full_cv_url):
                print("ok")
                break
            time.sleep(TIME_SLEEP)
        page += 1
        time.sleep(TIME_SLEEP)
    return _cv_list  # 返回二维cv号列表


def get_img(cv_url):
    """
    图片下载保存
    from https://blog.csdn.net/weixin_43920680/article/details/108550920
    :param cv_url: 完整专栏url
    :return:
    """

    img_list = []
    chrome.get(cv_url)

    try:
        chrome.find_element(By.CSS_SELECTOR, '.title-container h1')
        is_cv_exist = True
    except:
        is_cv_exist = False

    if is_cv_exist:
        head = chrome.find_element(By.CSS_SELECTOR, '.title-container h1').text
        time.sleep(TIME_SLEEP)
        WebDriverWait(chrome, 10).until(
            scroll,
            'scroll timeout'
        )
        print(head)
        imgs = chrome.find_elements(By.CSS_SELECTOR, '.normal-article-holder figure')
        if imgs:
            for img in imgs:
                try:
                    i = img.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    print(i)
                    img_list.append(i)
                except:
                    print("该元素非图片")
            os.mkdir(IMG_PATH + head)
            path2 = IMG_PATH + head + "\\"
            x = 1
            for img_url in img_list:
                s = '%04d' % x
                time.sleep(TIME_SLEEP)
                file_name_raw = head + str(s)
                file_name_extension = file_name_raw + ".jpeg"
                with open(path2 + file_name_extension, 'wb') as f:
                    response = requests.get(img_url)
                    f.write(response.content)
                img_jpeg = Image.open(path2 + file_name_extension)
                img_jpeg.load()
                img_jpeg.save(path2 + file_name_raw + ".png")
                os.remove(path2 + file_name_extension)
                print("成功爬取%d" % x + head)
                x += 1
            print("爬取结束")
            return True
        else:
            print("此cv不含图片")
            return True
    else:
        print("此cv不存在")
        return True


if __name__ == '__main__':
    cv_list = []  # 初始化一个cv_list
    # UID = '23155887'  # 修改UID号
    # UID = '1209981166'
    find_cv_number(cv_list, UID)
    chrome.quit()


