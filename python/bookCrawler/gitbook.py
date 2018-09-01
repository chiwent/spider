# coding=utf-8

# Inspired by: https://github.com/lzjun567/crawler_html2pdf/blob/master/pdf/crawler.py?1535807079455

import os
#from lxml import etree
import time
import sys
import requests
import pdfkit
from bs4 import BeautifulSoup
import re

#change the cookie value
headers = {
	"cookie": "xxx",
	"referer": sys.argv[1],
	"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
}

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>
"""

class Crawler(object):
	name = None
	def __init__(self, name, start_url):
		self.name = name
		self.start_url = start_url
		self.domain = '{0}://{1}'.format(str(start_url.split('://')[0]), str(start_url.split('://')[1]))
		
	@staticmethod
	def request(url, **kwrags):
		try:
			response = requests.get(url, **kwrags)
			return response
		except Exception as e:
			print("Error0:", e)
			return None
	
	def parse_menu(self, response):
		raise NotImplementedError
		
	def parse_body(self, response):
		raise NotImplementedError
		
	def run(self):
		start = time.time();
		options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'cookie': [
                ('cookie-name1', 'cookie-value1'),
                ('cookie-name2', 'cookie-value2'),
            ],
            'outline-depth': 10,
        }
		first_page = self.request(self.start_url, headers=headers, timeout=8)
		print('first_page status_code:', first_page.status_code)
		single_page = list(self.parse_menu(first_page))
		#print('single page:', single_page)
		all_page = list(set(single_page))
		all_page.sort(key = single_page.index)
		#print('all page:', all_page)
		htmls = []
		for index, url in enumerate(all_page):
			print('url:', url)
			body = self.request(url, headers=headers, timeout=8)
			if body:
				html = self.parse_body(body)
				#print('html:', html)
				f_name = ".".join([str(index), "html"])
				with open(f_name, 'wb') as f:
					f.write(html)
				htmls.append(f_name)
				#htmls = list(set(htmls))
			else:
				print('There is a error with: ', url)
			
		pdfkit.from_file(htmls, self.name + ".pdf", options=options)
		for html in htmls:
			os.remove(html)
		total_time = time.time() - start
		print('Use: %f' % total_time)

class Gitbook(Crawler):
	def parse_menu(self, response):
		soup = BeautifulSoup(response.content, 'lxml')
		try:
			menu = soup.find_all('li',attrs={'data-path': True})
			if menu is None:
				return None
			#menu_a = []
			#menu = list(set(menu))
			for item in menu:
				if item.find('a'):
					href = sys.argv[1] + item.find('a').attrs['href']
					#menu_a.append(href)
					yield href
		except Exception as e:
			print('Error1:', e)
			pass

		
	def parse_body(self, response):
		soup = BeautifulSoup(response.content, 'lxml')
		try:
			title = soup.find('h1', attrs={'id': True}).get_text()
			print('title:', title)
			body = soup.find('section', class_="normal markdown-section")
			center_tag = soup.new_tag("center")
			title_tag = soup.new_tag('h1')
			title_tag.string = title
			center_tag.insert(1, title_tag)
			body.insert(1, center_tag)
			html = str(body)
			pattern = "(<img .*?src=\")(.*?)(\")"
			
			def func(m):
				if not m.group(2).startswith("https"):
					rtn = "".join([m.group(1), self.domain, m.group(2), m.group(3)])
					return rtn
				else:
					return "".join([m.group(1), m.group(2), m.group(3)])
				
			html = re.compile(pattern).sub(func, html)
			html = html_template.format(content=html)
			html = html.encode('utf-8')
			return html
		except Exception as e:
			print('Error2:', e)
			pass
if __name__ == '__main__':
	argv = sys.argv
	start_url = argv[1]
	name = argv[2]
	if start_url.endswith('content/') is False:
		print('The start_url should like https://xxx.gitbooks.io/book_name/content/')
		sys.exit()
	if start_url.endswith('/') is False:
		start_url = start_url + '/'
	if start_url is None or name is None:
		print('please input like python3 gitbook.py url book_name')
		sys.exit()
	print('Book name:', name)
	print(start_url)
	crawler = Gitbook(name, start_url)
	crawler.run()
						
			
