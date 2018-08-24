#coding=utf-8


import requests
import os
import sys
from lxml import etree
from bs4 import BeautifulSoup
import multiprocessing
import time

# for hotidolsiv.tk
# Usage: python3 spider_single.py url

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36", "Referer": sys.argv[1]}

def crawl_page(url):
    try:
        res = requests.get(url, headers=headers, timeout=6)
        
    except Exception as e:
        return None
    content = res.content
    soup = BeautifulSoup(content, 'lxml')
    title = soup.find('h1',  class_='page-title').find('span').text
    path = os.path.abspath('.')
    print(title)
    folder_path =  path + '/' + str(title) + '/'
    if os.path.exists(folder_path) == False:  # judge folder exist
        os.makedirs(folder_path)  # mkdir
    os.chdir(folder_path)    # change path
    p = soup.find_all('p', class_='separator')
    img_src = []
    for index,item in enumerate(p):
        if item.find('img'):
            _ = item.find('img').attrs['src']
        img_src.append(_)
    return img_src
    

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

def download_img(url,ind):
    items = url
    for index,item in enumerate(items):  
        if item:
            # print('prepare download single img')
            html = requests.get(item, headers=headers, timeout=6)
            print('status code:',html)   
            img_name =  str(ind) + '-' +  str(index) +  '.jpg'
            with open(img_name, 'wb') as file:  # 
                file.write(html.content)  
                file.flush()  
            file.close()  
            print('The %d img downloaded successfully' %(index+1))  
            time.sleep(1) 

if __name__ == '__main__':
    n = 8
    argv = sys.argv 
    if (argv[1] is None):
        print('please input the url')
        sys.exit()
    src = crawl_page(argv[1])
    result = div_arr(src, n)
    # print(result)
    process = []
    for i in range(n):
        src = result[i]
        p = multiprocessing.Process(target=download_img,args=(src,i))
        p.start()
        process.append(p)
    for p in process:
        p.join()
    print('all subprocess done')


