#!/usr/bin/env python
# coding: utf-8

import os
import time
import json
import requests
from bs4 import BeautifulSoup

def find_urls(page_url):
    page = requests.get(page_url, headers=agent)
    tags = BeautifulSoup(page.content, features='xml').find_all('loc')
    urls = [tag.text for tag in tags]
    return urls

def get_content(url):
    page = requests.get(url, headers=agent)
    soup = BeautifulSoup(page.content, 'html.parser')
    content_dict = {'date': soup.find('div', class_='story-postdate').text,
                    'title': soup.find('h1', class_='headline node-title').text,
#                     'author': soup.find('em').text,
                    'text': soup.find('div', class_='ds-wrapper article-content-rawhtml').text}
    return content_dict

url_fpath = '../data/news/st_10delay/urls.txt'
news_fdir = '../data/news/st_10delay/'

agent = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33'}
sitemap_url = 'https://www.straitstimes.com/sitemap.xml'

# Scraping urls from the sitemap
if os.path.exists(url_fpath):
    with open(url_fpath, 'r') as f:
        urls = f.read().split('\n')
    last_idx = int(sorted(os.listdir(news_fdir), reverse=True)[1][:8])
    print('List of URLs already exists. Scraping continues from %d-th page.' % (last_idx + 1))
else:
    post_urls = [url for url in find_urls(sitemap_url)]

    urls = []
    for idx, post_url in enumerate(post_urls):
        print('Scraping urls from %d-th page out of %d pages...' % (idx+1, len(post_urls)), end='\r')
        urls += find_urls(post_url)

        time.sleep(10)
        
    print('\nScraping %d urls: Done' % len(urls))

    with open(url_fpath, 'w') as f:
        f.write('\n'.join(urls))
    print('Saving urls at: %s' % url_fpath)


    last_idx = -1

# Scraping contents from the urls
for idx, url in enumerate(urls):
    if idx <= last_idx:
        continue
    
    print('Scraping contents from %d-th url out of %d urls...' % (idx+1, len(urls)), end='\r')
    try:
        content = get_content(url)
        fname = news_fdir + '%.8d.json' % idx
        with open(fname, 'w') as f:
            json.dump(content, f, indent=4)
    except:
        continue
    
    time.sleep(10)
print('\nScraping contents: Done')
