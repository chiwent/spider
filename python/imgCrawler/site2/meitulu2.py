#meitulu.py
#coding=utf-8

# for meitulu.com --- crawl a single page
# use： python3 meitulu2.py <singel page>(like:https://www.meitulu.com/item/12629.html)

import requests
from bs4 import BeautifulSoup
import os
import sys
import time
import multiprocessing


#reload(sys)  
#sys.setdefaultencoding('utf8')  

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36", "Referer": sys.argv[1]}

"""
def remove_first_and_final(arr):
    leng = len(arr)
    arr.pop()
    arr.pop(0)
"""
img_src_list = []
def crawl_page(url):
    res = requests.get(url, headers=headers)
    content = res.content
    soup = BeautifulSoup(content, 'lxml')
    title = soup.find('div', class_='weizhi').find('h1').string
    path = os.path.abspath('.')
    folder_path = path + '/img/' + str(title) + '/'
    print(folder_path)
    if os.path.exists(folder_path) == False:  # 判断文件夹是否已经存在  
        os.makedirs(folder_path)  # 创建文件夹
    os.chdir(folder_path)
    first_img = soup.find('div', class_='content').find_all('img')
    first_img_list = []
    for index,item in enumerate(first_img):
        _ = item.attrs['src']
        first_img_list.append(_)
    a = soup.find('div', id='pages').find_all('a')
    all_pages_num = int(a[-2].string)
    pages = []
    a.pop()
    a.pop(0)
    
    a = ['https://www.meitulu.com' + str(item.attrs['href']) for item in a]
    img_src_list = []
    for i in a:
        r = requests.get(i, headers=headers)
        con = r.content
        soup = BeautifulSoup(con, 'html.parser')
        img_list = soup.find('div', class_='content').find_all('img')
        for index,item in enumerate(img_list):
            _ = item.attrs['src']
            img_src_list.append(_)
    img_src_list.extend(first_img_list)
    return img_src_list

def download_img(url,ind):
    items = url
    #print(items)

    for index,item in enumerate(items):  
        if item:          
            html = requests.get(item, headers=headers)
            print('status code:',html)    
            img_name =  str(ind) + '-' +  str(index) +  '.jpg'
            with open(img_name, 'wb') as file:  # 以byte形式将图片数据写入  
                file.write(html.content)  
                file.flush()  
            file.close()  # 关闭文件  
            print('第%d张图片下载完成' %(index+1))  
            time.sleep(1)  # 自定义延时  
    #print('抓取完成') 

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
    if url is None:
        print('请输入网址')
    n = 8 #进程数
    html = crawl_page(url)
    #print('all img src:',html,'\n\n')
    res = div_arr(html,n)
    process = []
    for i in range(n):
        src = res[i]
        p = multiprocessing.Process(target=download_img,args=(src,i))
        p.start()
        process.append(p)
    for p in process:
        p.join()
    print('all subprocess done')
