#coding=utf-8


# tu_chong spider for a user's site
# Usage: python3 spider1.py url

import requests
from lxml import etree
# from bs4 import BeautifulSoup
import json
import os
import sys
import time
# import multiprocessing
from multiprocessing import Pool, Queue
import re
import math


headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "referer": sys.argv[1],
    "user-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36"
}


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
            res = requests.get(url, headers=headers, timeout=7)
            print(res.status_code)
            res = res.content
            html = etree.HTML(res)
            page = html.xpath(path, stream=True)
            return page
        except Exception as e:
            print('Error1:', e)
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

def download_img(url):
    
    for index,item in enumerate(url):  
        if item:
            try:          
                html = requests.get(item, headers=headers, timeout=8)
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

def get_authorid(url):
    try:
        req = requests.get(url, headers=headers, timeout=8)
        pattern = re.compile('\{\"site_id\":\"(\d+)\"')
        text = pattern.search(req.text)
        authorid = text.group(1)
        return authorid
    except Exception as e:
        print('Error1:', e)
        sys.exit()

flag = True
if __name__ == '__main__':
    n = 4
    argv = sys.argv
    url = argv[1]
    global flag
    if url is None:
        print('you should input the url like: https://tuchong.com/1601417/')
        sys.exit()
    if not url.endswith('/'):
        url = url + '/'
    # folder_name = re.compile('(https|http):\/\/(.*?).tuchong.com\/').search(url) ? re.compile('(https|http):\/\/(.*?).tuchong.com\/').search(url) : url.split('.com/')[1].split('/')[0]
    username = re.compile('(https|http):\/\/(.*?).tuchong.com').search(url).group(2)
    if username is None:
        flag = False
        username = url.split('.com/')[1].split('/')[0]
    folder_path =  os.getcwd() + '/' + str(username) + '/'
    if os.path.exists(folder_path) == False:
        os.makedirs(folder_path)  
    os.chdir(folder_path)
    index = 1
    authorid = get_authorid(url)
    #request_url = url + '/rest/2/sites/' + authorid + '/posts?count=20&page={0}&before_timestamp'.format(index)
    while True:
        try:
            if flag:
                request_url = url + 'rest/2/sites/' + authorid + '/posts?count=20&page={0}&before_timestamp'.format(index)
            else:
                request_url = 'https://tuchong.com/rest/2/sites/' + authorid + '/posts?count=20&page={0}&before_timestamp'.format(index)
            print('request_url:', request_url)
            req = requests.get(request_url, headers=headers, timeout=8)
            # if (req.status_code is 404):
            #     print('all have done..')
            #     sys.exit()
            index += 1
            # req.encoding = 'utf-8'
            jsondata = req.content.decode()
            # print('jsondata:', jsondata)
            if json.loads(jsondata)["more"] is False:
                print('all have done..')
                sys.exit()
            data = json.loads(jsondata)["post_list"]
            img_src = []
            for item1 in data:
                for item2 in item1['images']:
                    source = item2['source']['lr']
                    print('source:', source)
                    img_src.append(source)
            src = div_arr(img_src, n)
            pool = Pool(processes=n)
            datas = (data for data in src)
            pool.map(download_img, datas)
            pool.close()
            pool.join()
        except Exception as e:
            print('Error:', e)
            pass


        

