import os
import re
from pyvirtualdisplay import Display
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import csv
import requests
import math
import time
import uuid
import hashlib
import pickle
from random import randint
from time import sleep


class Audioblocks:
    def __init__(self):
        self.initialize()
        self.main()

    def load_url(self, url):

        
        self.browser.get(f'https://www.audioblocks.com{url}')
        # self.browser.get(f'https://www.audioblocks.com/stock-audio/redaction-and-revision-percussion-05-125bpm-01-rgb8ep03lwbk0wy5vbm.html')
        # self.browser.get(f'https://www.audioblocks.com/stock-audio/idm-loop-140355.html')

        submit_button = self.browser.find_elements_by_xpath('//*[@id="details-app-container"]/div/div/div[1]/div[1]/div[1]/div[1]/div/section/div[1]/div[1]')[0]
        submit_button.click()

        audio_file_path = self.get_audio_file_path()
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        media_preview = soup.find("div", {"class": "mediaPreview"})

        self.download(audio_file_path)
        self.get_data_from_item_page(media_preview, url, audio_file_path)

    def main(self):
        data = self.get_pickle("audio_pages.pickle")

        file = "/code/page_cache.pickle"
        cache = self.get_pickle(file)
        for url_hash in data:
            if url_hash not in cache:
                sleep(randint(1,3))
                page = data[url_hash]
                self.load_url(page.get('url'))
                cache[url_hash] = True
                self.save_pickle(file, cache)
            
    def __del__(self):
        self.browser.quit()
        self.display.stop()

    def initialize(self):
        self.display = Display(visible=0, size=(1200, 800))
        self.display.start()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1200x800")
        self.browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='/usr/bin/chromedriver')


    def get_audio_file_path(self):
        # audio = self.browser.find_elements_by_xpath('//*[@id="audio"]')
        audio = self.browser.find_element_by_tag_name('audio').get_attribute('src')
        return audio

    
    def get_url(self, elem):
        url = elem.find("div", {"class": "item-title-wrapper"}).find('a')['href']
        return url 
    
    
    def get_author(self, elem):
        url = elem.find("div", {"class": "artist-wrapper"})
        if url is None:
            return ''
        return url.find('a').getText()

    
    def url_encode(self, url):
        result = hashlib.md5(url.encode('utf-8')) 
        return result.hexdigest()

    
    def get_title(self, elem):
        url = elem.find("div", {"class": "item-title-wrapper"}).getText()
        return url 

    
    def get_tags(self, elem):
        tags = [ e.getText() for e in elem.findAll("a", {"class": "tag"})]
        tags += [ e.getText() for e in elem.findAll("span", {"class": "media-type-tag"})]
        return tags 

    
    def get_pickle(self, file):
        try: 
            pickle_in = open(file,"rb")
        except:
            return {}
        return pickle.load(pickle_in)

    
    def save_pickle(self, file, data):
        pickle_out = open(file, "wb")
        pickle.dump(data, pickle_out)
        pickle_out.close()
        return True

    def get_data_from_collection_page(self, soup, collection):      
        stock_items = soup.findAll("section", {"class": "stock-item"})
        file = "audio_pages.pickle"
        data = self.get_pickle(file)
        for count, stock_item in enumerate(stock_items):
            
            url = self.get_url(stock_item)
            data[self.url_encode(url)] = {
                'id': self.url_encode(url),
                'url': url,
                'collection': collection
            }
        self.save_pickle(file, data)                    

    
    def get_html(self, url):
        r  = requests.get(url)
        return r.text

    
    def get_meta(self, stock_meta):
        meta = {}
        for count, stock_item in enumerate(stock_meta):
            meta[stock_item.find("span", {"class": 'stockItemInfo-stockSpecItemKey'}).getText()] = stock_item.find("span", {"class": 'stockItemInfo-stockSpecItemValue'}).getText()
        return meta

    def download(self, url):
        """
        Get filename from content-disposition
        """
        if not url:
            return None
        
        r = requests.get(url, allow_redirects=True)
        filename = os.path.basename(url)
        open('/code/audio/'+filename, 'wb').write(r.content)


    def get_urls_from_collection(self, url:str, page_size:int, collection:str):
        for n in range(math.ceil(int(page_size)/48)):
            url_temp = url
            url_temp = f"{url_temp}?page={n+1}"
            file = "collection_cache.pickle"
            collection_cache = self.get_pickle(file)
            if url_encode(url_temp) not in collection_cache:
                time.sleep(2.4)
                data = get_html(url_temp)
                soup = BeautifulSoup(data)
                get_data_from_collection_page(soup, collection)
                collection_cache[url_encode(url_temp)] = True
                print(f"Done for {url_temp}")
            else:
                print(f"from Cache {url_temp}")
                
            self.save_pickle(file, collection_cache)

    def get_data_from_item_page(self, media_preview, url, mp3_file):
        stock_items = media_preview.findAll("section", {"class": "stock-item"})
        stock_meta = media_preview.findAll("li", {"class": "stockItemInfo-stockSpecItem"}) 
        
        # sfx = self.get_sfx(media_preview)

        file = "/code/audio_pages.pickle"
        data = self.get_pickle(file)
        url_hash = self.url_encode(url)

        for stock_item in stock_items:
            data[url_hash]['title'] =  self.get_title(stock_item)
            data[url_hash]['author'] = self.get_author(stock_item)
            data[url_hash]['tags'] = self.get_tags(stock_item)
            # data[url_hash]['tags'].append(sfx)
            data[url_hash]['meta'] = self.get_meta(stock_meta)
            data[url_hash]['mp3'] = mp3_file
        self.save_pickle(file, data)

