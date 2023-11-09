# coding: utf-8

import os
import re
import time
import json
import requests

from bs4 import BeautifulSoup


news_fdir = '../data/raw/news/bbc/'
url_fpath = news_fdir + 'urls.txt'

agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

sitemap_url = 'https://www.bbc.com/sitemaps/https-index-com-archive.xml'


def find_urls(page_url):
    page = requests.get(page_url, headers=agent)
    elements = BeautifulSoup(page.content, features='xml').find_all('loc')
    urls = [element.text for element in elements]
    return urls

def get_content(url):
    page = requests.get(url, headers=agent)
    soup = BeautifulSoup(page.content, 'html.parser')

    date = soup.find('time', {'data-testid': 'timestamp'}).text
    title = soup.find('h1', id='main-heading').text
    text = ' '.join([element.text for element in soup.find_all('div', \
        {'data-component': 'text-block'})])
    text = re.sub(r'[\s]+', ' ', text)

    content_dict = {'date': date,
                    'title': title,
                    'text': text}
    return content_dict

def scrape_sitemap(sitemap_url, re_scrape=False):
    url_fpath = news_fdir + 'urls.txt'
    if os.path.exists(url_fpath) and not re_scrape:
        print('List of URLs already exists. Loading the URL list...')
        
        with open(url_fpath, 'r') as f:
            url_list = f.read().split('\n')
        print('Loading URL list: Done\n')
    
    else:
        print('Scraping sitemap starts from the scratch.')
        page_list = find_urls(sitemap_url)

        url_list = []
        for idx, page in enumerate(page_list):
            print('Scraping %d-th page from the root sitemap, out of total %d pages...' % \
                (idx+1, len(page_list)), end='\r')
            
            url_list += [url for url in find_urls(page) \
                if url.startswith('https://www.bbc.com/news/')]
        print('\nScraping sitemap: Done\n')

        print('Saving URLs list at: %s' % url_fpath)
        os.makedirs(news_fdir, exist_ok=True)
        with open(url_fpath, 'w') as f:
            f.write('\n'.join(url_list))
        print('Saving URLs list: Done\n')

    return url_list

def scrape_urls(url_list):
    print('Scarping total %d URLs starts.' % len(url_list))
    file_list = os.listdir(news_fdir)
    if len(file_list) <= 1:
        last_idx = -1
        print('Scraping URLs starts from the scratch.\n')
    else:
        last_idx = int(sorted(file_list, reverse=True)[1][:8])
        print('Scraping URLs continues from %d\n' % last_idx)

    for idx, url in enumerate(url_list):
        if idx <= last_idx:
            continue
        
        print('Scraping contents from %d-th URL out of %d URLs...' % \
            (idx+1, len(url_list)), end='\r')
        try:
            content = get_content(url)
            
            fname = news_fdir + '%.8d.json' % idx
            with open(fname, 'w') as f:
                json.dump(content, f, indent=4)
        
        except Exception:
            continue
        
        time.sleep(0.1)
    print('\nScraping contents: Done\n')

    return

def main():
    url_list = scrape_sitemap(sitemap_url, re_scrape=False)
    scrape_urls(url_list)
    
    return


if __name__ == '__main__':
    main()