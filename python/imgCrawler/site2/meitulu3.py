#coding=utf-8

# Download all of a model's pictures
# use： python3 meitulu3.py <tag page>(like:  https://www.meitulu.com/t/ebeinaicha/) <son page number>

import requests
import os
import sys
from lxml import etree
import multiprocessing
import time
import numpy as np

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36", "Referer": 'https://www.meitulu.com/'}
#headers2 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36", "Referer": refer}

def crawl_main_page(url):
    res = requests.get(url, headers=headers, timeout=2)
    content = res.content
    html = etree.HTML(content)
    page = html.xpath('/html/body/div[2]/div[3]/ul/li/a',stream=True)
    hrefs = []
    for i in page:
        href = i.attrib['href']
        hrefs.append(href)
    hrefs = sorted(hrefs)[::-1]

    num = int(sys.argv[2])
    if num < len(hrefs):
        hrefs = hrefs[:num]
    return list(set(hrefs)) #去重


all_list = []
aa = []
title = []
def crawl_signel_page(url):
    # print(url)
    for i in url:
        print('crawling  ',i,'  now','\n\n')
        home_page = i.split('/')[-1].split('.')[0]
        res = requests.get(i, headers=headers, timeout=2)
        content = res.content
        html = etree.HTML(content)
        ti = html.xpath('/html/body/div[2]/div[1]/h1')[0].text
        title.append(ti)
        html = html.xpath('//*[@id="pages"]/a', stream=True)
        max_page = int(html[-2].text)
        html.pop()
        html.pop(0)
        a = []
        a.append(str(i))
        others = ['https://www.meitulu.com' + str(item.attrib['href']) for item in html]
        a.extend(others)
        aa.append(a)
    all_img_list = []
        # k = 0
    for i in aa:
        all_img_list = find_signel_img(i)
        all_list.append(list(all_img_list))
    with open('list6.txt', 'w') as file:
        file.write(str(all_img_list))
        file.flush()
    file.close()

    return all_list,title

def find_signel_img(url):
    img_src_list = []
    for i in url:
        r = requests.get(i, headers=headers)
        con = r.content
        img = etree.HTML(con)
        img = img.xpath('/html/body/div[4]/center/img', stream=True)
        for index,item in enumerate(img):
            _ = item.attrib['src']
            img_src_list.append(str(_))
    img_src_list = set(img_src_list)  #去重
    with open('list4.txt','w') as file:
        file.write(str(img_src_list))
        file.flush()
    file.close()

    return img_src_list 

def download_img(url,ind):
    for index,item in enumerate(url):  
        if item:
            refer = 'https://www.meitulu.com/item/' + str(str(item).split('/')[-2]) + '.html'
            headers2 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36", "Referer": refer}
            html = requests.get(item, headers=headers2)
            print('status code:',html)    
            img_name =  str(ind) + '-' +  str(index) +  '.jpg'
            with open(img_name, 'wb') as file:  # 以byte形式将图片数据写入  
                file.write(html.content)  
                file.flush()  
            file.close()  # 关闭文件  
            print('第%d张图片下载完成' %(index+1))  
            time.sleep(1)  # 自定义延时
    #os.chdir('../')  

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


if __name__ == '__main__':
    argv = sys.argv
    url = argv[1]
    nums = argv[2]
    if url is None:
        print('请输入网址')
    n = 8 #进程数
    html = crawl_main_page(url)
    try:
        pages,title = crawl_signel_page(html)
    except e as Exception:
        pass
    with open('list5.txt', 'w') as file:
        file.write(str(pages))
        file.flush()
    file.close()
    for i in range(int(nums)):
        result = []
        res = div_arr(pages[i],n)
        result.append(res)
        with open('list6.txt', 'w') as file:
            file.write(str(result))
            file.flush()
        file.close()
        process = []
        path = os.path.abspath('.')
        print(title[i])
        folder_path =  path + '/' + str(title[i]) + '/'
        if os.path.exists(folder_path) == False:  # 判断文件夹是否已经存在  
            os.makedirs(folder_path)  # 创建文件夹
        os.chdir(folder_path)    # 切换文件夹
        for j in range(n):
            src = result[0][j]
            p = multiprocessing.Process(target=download_img,args=(src,j))
            p.start()
            process.append(p)
        for p in process:
            p.join()
        os.chdir('../')
        print('all subprocess done')






