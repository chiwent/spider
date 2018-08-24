#coding=utf-8


# Download a classified album like https://www.nvshens.com/gallery/ysweb/

#Usage: 
# python3 spider.py https://www.nvshens.com/gallery/ysweb/ beginIndex endIndex
# note: If you just want to download the content of a web page, such as the second page, the 'beginIndex' and 'endIndex' should be '2'

import requests
from lxml import etree
import os
import sys
import time
import multiprocessing
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
            time.sleep(0.5)
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

def crawl_main_page(page):
    try:
        res = requests.get(page, headers=headers, timeout=7).content
    except Exception as e:
        print('Error')

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
    
    for item1 in url:
        img_src = list()
        title = get_title(item1)
        path = os.path.abspath('/media/simon/新加卷1/codetest/test/python/spider/nvshens.com')
        folder_path =  path + '/' + str(title) + '/'
        if os.path.exists(folder_path) == False:  # 判断文件夹是否已经存在  
            os.makedirs(folder_path)  # 创建文件夹
        os.chdir(folder_path)    # 切换文件夹
        time.sleep(0.5)
        single_page_img_nums = len(crawl(item1, '//*[@id="hgallery"]/img'))
        nums = int(get_nums(item1))
        nums = math.ceil(nums/single_page_img_nums)
        single_nav = []
        for num in range(nums):
            num = str(num + 1)
            page = item1 + num + '.html'
            single_nav.append(page)
        print('single_nav:', single_nav)
        for item2 in single_nav:
            img = crawl(item2, '//*[@id="hgallery"]/img')
            src = []
            for i in img:
                src.append(i.attrib['src'])
                img_src.append(src)
        img_src = list(set(flatten(img_src)))
        print('single_page_src2:', img_src)
        for index,item in enumerate(img_src):  
            if item:
                try:          
                    html = requests.get(item, headers=headers, timeout=8)
                    # print('img_status: ', html.status_code)
                    html = html.content
                except Exception as e:
                    print('Error4: ', e)   
                    return None
                img_name =  str(index) + str(item.split('/')[-1])
                with open(img_name, 'wb') as file:  # 以byte形式将图片数据写入  
                    file.write(html)  
                    file.flush()  
                file.close()  # 关闭文件  
                print('第%d张图片下载完成' %(index+1))  
                time.sleep(1)  # 自定义延时  

if __name__ == '__main__':
    
    n = 8
    argv = sys.argv
    url = argv[1]
    begin = int(argv[2])
    end = int(argv[3])
    if argv[0] is None or argv[1] is None or argv[2] is None:
        print('cheeck your params: python3 url begin-index end-index')
        sys.exit()
    main_url = []
    for i in range(begin, end+1):
        i = str(i)
        main_url.append(url + i + '.html')    
    if begin is 1:
        main_url.pop(0)
        main_url.append(url)
    main_gallery = []
    for item in main_url:
        _ = crawl(item, '//*[@id="listdiv"]/ul/li/div[1]/a')
        main_gallery.append(_)
    main_gallery_a = []
    for item1 in main_gallery:
        for item2 in item1:
             main_gallery_a.append(ref + item2.attrib['href'])
    div_a = div_arr(main_gallery_a, n)

    process = []
    for i in range(n):
        arr = []
        arr.append(div_a[i])
        p = multiprocessing.Process(target=download_img,args=arr)
        p.start()
        process.append(p)
    for p in process:
        p.join()

