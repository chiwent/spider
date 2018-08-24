#coding=utf-8
import requests   
from bs4 import BeautifulSoup  
import os  
import time  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException
#from lxml import etree
import sys
import multiprocessing


# for a single page in http://www.mmjpg.com/
# Usage: python3 mmjpg.py url

headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
            , "Connection": "keep-alive", 'Referer':'http://www.mmjpg.com/'
         }

items = []
def phant(url):
    driver = webdriver.PhantomJS(executable_path="D:/python3.6.4/phantomjs-2.1.1-windows/bin/phantomjs.exe")
    wait = WebDriverWait(driver,10)
    driver.set_window_size(1120, 550)
    driver.get(url)
    submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#opic')))
    #print(submit)
    #submit.click() #无效

    driver.execute_script('document.getElementById("opic").click()')

    time.sleep(1)

    # lastHeight = driver.execute_script("return document.body.scrollHeight")
    # while True:
    # 	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # 	time.sleep(1)
    # 	newHeight = driver.execute_script("return document.body.scrollHeight")
    # 	if newHeight == lastHeight:
    # 		break
    # 	lastHeight = newHeight
    	#print(lastHeight)
    #element = driver.find_element_by_id('content')
    # js = "var q = document.documentElement.scrollTop=10000"
    # driver.execute_script(js)
    #time.sleep(1)
    html = driver.page_source
    driver.quit()
    return html


def crawl_html(html):
    soup = BeautifulSoup(html, 'lxml')
    #global title  #全局变量无法传入多进程操作
    title = soup.find('div', class_='article').find('h2').string
    itemss = soup.find_all("div", id="content")
    print('itemss:',itemss,'\n\n')
    #items = []
    for item in itemss:
    	img = item.find_all("img")
    	#print(img)
    	for i in img:
    		im = i.attrs['data-img']
    		#img = img.find(attrs={})
    		items.append(im)
    print('items:',items)
    folder_path = './mmjpg/' + title + '/'
    path = os.getcwd()
    if os.path.exists(folder_path) == False:  # 判断文件夹是否已经存在  
        os.makedirs(folder_path)  # 创建文件夹
    os.chdir(path + folder_path)	# 切换文件夹

def div_list(ls,n):  
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

def get_img(res,ind):
    """
    folder_path = './mmjpg/' + title + '/'
    if os.path.exists(folder_path) == False:  # 判断文件夹是否已经存在  
        os.makedirs(folder_path)  # 创建文件夹
    print('download path:',folder_path)  
    """
    items = res
    print(items)

    for index,item in enumerate(items):  
        if item:          
            html = requests.get(item, headers=headers)    
            img_name = str(ind) + '-' + str(index + 1) +'.jpg'  
            with open(img_name, 'wb') as file:  # 以byte形式将图片数据写入  
                file.write(html.content)  
                file.flush()  
            file.close()  # 关闭文件  
            print('第%d张图片下载完成' %(index+1))  
            time.sleep(1)  # 自定义延时  
    print('抓取完成') 

if __name__ == '__main__':
    argv = sys.argv
    url = argv[1]
    if url is None:
        print('请输入网址')
    n = 8 #进程数
    html = phant(url)
    crawl_html(html)
    res = div_list(items, n)
    #print('Path:',os.getcwd())
    process = []
    for i in range(n):
        src = res[i]
        p = multiprocessing.Process(target=get_img,args=(src,i,))
        p.start()
        process.append(p)
    for p in process:
        p.join()
    print('all subprocess done')
    
