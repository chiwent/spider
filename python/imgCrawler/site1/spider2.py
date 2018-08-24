#coding=utf-8

# Download all of a model's pictures

#Usage:
#  python3 spider2.py https://www.nvshens.com/girl/24282/ or python3 spider2.py https://www.nvshens.com/girl/25361/


# TODO: 
# 

import requests
from lxml import etree
import os
import sys
import time
# import multiprocessing
from multiprocessing import Pool
import re
import math
# import numpy as np

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36", "Referer": 'http://www.996mb.com/',"Connection":"close"}

ref = 'https://www.nvshens.com'

class retry(object):
    def __init__(self,*,times):
        self._cnt=times
    def __call__(self,func):
        def wrapper(*args,**kw):
            data=None
            cnt=self._cnt
            while data==None and cnt>0:
                data=func(*args,**kw)
                cnt-=1
                print('重新请求')
            return data
        return wrapper


def crawl(url, path):
    
    if url:
        try:
            time.sleep(0.1)
            # requests.adapters.DEFAULT_RETRIES = 3
            # s = requests.session()       
            # s.keep_alive = False
            res = requests.get(url, headers=headers, timeout=7)
            print(res.status_code)
            res = res.content
            html = etree.HTML(res)
            page = html.xpath(path, stream=True)
            # if html.xpath('//*[@id="htilte"]', stream=True):
            #     title = html.xpath('//*[@id="htilte"]', stream=True)[0].text
            return page
            # print(res)
        except Exception as e:
            print('Error1:', e)
            pass
       
        # page.pop()

def get_title(url):
    
    if url:
        try:
            res = requests.get(url, headers=headers, timeout=7)
            res = res.content
            html = etree.HTML(res)
            if html.xpath('//*[@id="htilte"]', stream=True):
                title = html.xpath('//*[@id="htilte"]', stream=True)[0].text
            return title
            # print(res)
        except Exception as e:
            print('Error2:', e)
            pass
def get_nums(url):
    
    if url:
        try:
            res = requests.get(url, headers=headers, timeout=7)
            res = res.content
            html = etree.HTML(res)
            if html.xpath('//*[@id="dinfo"]/span', stream=True):
                nums = re.match('\d{0,3}',html.xpath('//*[@id="dinfo"]/span', stream=True)[0].text).group()
                return nums
            # print(res)
        except Exception as e:
            print('Error3:', e)
            pass



def div_arr(ls,n):  
   result = []  
   cut = int(len(ls)/n)  
   if cut == 0:  
       ls = [[x] for x in ls]  
       none_array = [[] for i in range(0, n-len(ls))]  
       return ls+none_array  
   for i in range(0, n-1):  
       result.append(ls[cut*i:cut*(1+i)])  
   result.append(ls[cut*(n-1):len(ls)])  
   return result  

def flatten(a):
    if not isinstance(a, (list, )):
        return [a]
    else:
        b = []
        for item in a:
            b += flatten(item)
    return b

# def change_path(url):
    
# @retry(times=3)
def download_img(url):
    
    for index,item in enumerate(url):  
        if item:
            try:          
                html = requests.get(item, headers=headers, timeout=15)
                # print('img_status: ', html.status_code)
                html = html.content
            except Exception as e:
                print('Error4: ', e)
                pass   
                # return None
            img_name =  str(index) + str(item.split('/')[-1])
            with open(img_name, 'wb') as file:  # 以byte形式将图片数据写入  
                file.write(html)  
                file.flush()  
            file.close()  # 关闭文件  
            print('第%d张图片下载完成, name: %s' %(index+1, img_name))  
            time.sleep(1)  # 自定义延时  

if __name__ == '__main__':
    
    n = 8
    argv = sys.argv
    url = argv[1]
    if url is None:
        print('cheeck your params: python3 url')
        sys.exit()
    main_gallery = crawl(url, '//*[@id="photo_list"]/ul/li/div[1]/a') if re.match('.*?\/\d+\/\w+\/', url) else crawl(url, '//*[@id="post"]/div[8]/div/div[3]/ul/li/div[1]/a')
    # main_gallery = crawl(url, '//*[@id="post"]/div[8]/div/div[3]/ul/li/div[1]/a') ? crawl(url, '//*[@id="post"]/div[8]/div/div[3]/ul/li/div[1]/a')
    # print('main:',main_gallery)
    main_gallery_a = []
    for item in main_gallery:
        _ = ref + item.attrib['href']
        main_gallery_a.append(_)
    pages = int(len(main_gallery_a))
    path = os.getcwd()
    for item1 in main_gallery_a:
        img_src = list()
        single_page_img_nums = len(crawl(item1, '//*[@id="hgallery"]/img'))
        nums = get_nums(item1)
        nums = math.ceil(int(nums)/single_page_img_nums)
        single_nav = []
        for num in range(nums):
            num = str(num + 1)
            page = item1 + num + '.html'
            single_nav.append(page)
        for item2 in single_nav:
            img = crawl(item2, '//*[@id="hgallery"]/img')
            src = []
            for i in img:
                src.append(i.attrib['src'])
                img_src.append(src)
        img_src = list(set(flatten(img_src)))
        div_a = div_arr(img_src, n)

        title = get_title(item1)
        # path = os.path.abspath('.')
        folder_path =  path + '/' + str(title) + '/'
        if os.path.exists(folder_path) == False:  # 判断文件夹是否已经存在  
            os.makedirs(folder_path)  # 创建文件夹
        os.chdir(folder_path)    # 切换文件夹
        
        pool = Pool(processes=n)
        # datas = list()
        # datas.append(div_a[i])
        datas = (data for data in div_a)
        pool.map(download_img, datas)
        pool.close()
        pool.join()

        # process = []
        # for i in range(n):
        #     arr = []
        #     arr.append(div_a[i])
        #     p = multiprocessing.Process(target=download_img,args=arr)
        #     p.start()
        #     process.append(p)
        # for p in process:
        #     p.join()

