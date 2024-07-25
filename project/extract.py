import pandas as pd
import numpy as np
import time
import json
import os
import re
from dotenv import load_dotenv
from urllib.request import urlopen
from datetime import date
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
# from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from preprocessing import Preprocessing

today = date.today()

# INITIATE AND CALL THE BROWSER FOR SCRAPING
def webdriver_config():
    # SET THE HEADER
    # ua = UserAgent(verify_ssl=False)
    ua = UserAgent()
    userAgent = ua.random
    header = {'User-Agent': userAgent}
    # SET THE BROWSER OPTION 
    chrome_options = Options()
    chrome_options.add_argument("--headless") # comment this line to see the browser running
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--log-level=1")
    chrome_options.add_argument(f'user-agent={userAgent}')
    return chrome_options

def lppmunila_year():
    # CREATE LIST YEAR FOR URL
    # some years setting manually
    list_year = ['3276', '3018', '2107', '1985', '1977', '1010', '0223', '0220', '0214', '0207', '0202', '0201', '0200', '0029', '0028', '0022', '0021', '0020', '0017', '0016', '0015']
    for i in range(1990, 2025):
        list_year.append(str(i))
    list_year = sorted(list_year, reverse=True)
    # print(len(list_year))
    # urls = ['http://repository.lppm.unila.ac.id/cgi/exportview/year/2023/JSON/2023.js', 'http://repository.lppm.unila.ac.id/cgi/exportview/year/1990/JSON/1990.js'] # for testing
    urls = list_year

    # COLLECT DATA FROM EACH YEAR'S URL
    df = pd.DataFrame()
    for idx, url in enumerate(urls):
        url = f'http://repository.lppm.unila.ac.id/cgi/exportview/year/{url}/JSON/{url}.js'
        # print(url)
        dict = urlopen(url).read()
        dict = json.loads(dict)
        data = pd.json_normalize(dict)
        print(f"data {idx}: {len(data)}")
        df = pd.concat([df, data], ignore_index = True, axis = 0)

    # CLEAN DATA COLLECTION AND CONVERT INTO CSV
    columns = ['divisions', 'title', 'abstract', 'subjects', 'publication', 'publisher', 'eprintid', 'type', 'date', 'uri', 'official_url']
    pre_processing = Preprocessing()
    df[columns] = df[columns].replace(np.nan, '', regex=True)
    df[['divisions', 'title', 'abstract', 'subjects', 'publication', 'publisher', 'eprintid']] = df[['divisions', 'title', 'abstract', 'subjects', 'publication', 'publisher', 'eprintid']].map(lambda x:pre_processing.clean_text(x))
    df['uri'] = df['uri'].str.replace('\\', '')
    df['official_url'] = df['official_url'].str.replace('\\', '')
    print("Total data:", len(df[columns]))
    df[columns].to_csv(f"data/data_crawling_lppmunila_year_{today}.csv")

def gscholar_idauthor():
    # SETUP THE CHROME FROM THE FUNCTION
    chrome_options = webdriver_config() 
    driver = webdriver.Chrome(options=chrome_options)
    
    # ACCESS ARTICLE LINK FROM AUTHORS
    # list_idgs = ['sXyP1GYAAAAJ', 'SdfFZQYAAAAJ', 'x3ceWPkAAAAJ'] # manual list
    list_idgs = ['sXyP1GYAAAAJ'] # manual list
    articles = []
    for idgs in list_idgs:
        url_author = f"https://scholar.google.com/citations?user={idgs}"
        driver.implicitly_wait(50)
        driver.get(url_author)
        # access all link from the show more
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        initial_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            buttons = driver.find_element(By.XPATH, ".//div[@id='gs_bdy']//div[@id='gs_bdy_ccl']//div[@id='gsc_bdy']//div[@id='gsc_art']//form[input/@name='xsrf']//div[@id='gsc_lwp']//div[@id='gsc_bpf']//button[@id='gsc_bpf_more']")
            buttons.click()
            current_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(5)
            if initial_height != current_height:
                initial_height = current_height
            else:
                break
        soup = BeautifulSoup(driver.page_source, 'lxml')
        url_articles = []
        for a in soup.find_all('a', class_="gsc_a_at"):
            link_article = f"https://scholar.google.com/{a['href']}"
            # print(link_article)
            url_articles.append(link_article)
        print("Total articles: ", len(url_articles))

        # CRAWLING INFORMATION FROM EACH ARTICLE LINK INTO DICTIONARY, LIST, AND A FILE LATER
        # df = pd.DataFrame()
        for idx, url in enumerate(url_articles):
            # print(f"{idx}. {url}")
            dict = {}

            # obtain id author's google scholar 
            dict["idgs"] = idgs

            # obtain title
            response = requests.get(url, headers=header)
            soup = BeautifulSoup(response.content, 'lxml')
            title = soup.find("div",{"id":"gsc_oci_title"}).get_text()
            dict["title"] = title
            
            # obtain other informations
            fields = []
            for val in soup.findAll('div', attrs={'class':'gsc_oci_field'}):
                fields.append(val.text)
            values = []
            for val in soup.findAll('div', attrs={'class':'gsc_oci_value'}):
                values.append(val.text)
        
            for key in fields:
                for value in values:
                    dict[key] = value
                    values.remove(value)
                    break
            
            articles.append(dict)
            # print(str(dict))

    json_articles = json.dumps(articles, indent=4)
    # print(json_articles)

    # convert to json
    with open(f"data/data_crawling_gscholar_idauthor_{today}.json", "w") as outfile:
        outfile.write(json_articles)

class SintaExtract:

    # SET THE LIST
    title = []
    pub = []
    year = []
    quartile = []
    cited = []
    creator = []
    pub_type = []
    url = []
    id_sinta = []
    uri = []

    def __init__(self, uname, pw, ids):
        self.uname = uname
        self.pw = pw
        self.ids = ids
        # self.url = url

    def sinta_login(self):
        # open and setting the web driver chrome
        chrome_options = webdriver_config() 
        driver = webdriver.Chrome(options=chrome_options)
        # login
        driver.get("https://sinta.kemdikbud.go.id/logins")
        username = driver.find_element(By.NAME, "username")
        username.send_keys(self.uname)
        password = driver.find_element(By.NAME, "password")
        password.send_keys(self.pw)
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        return driver

    def sinta_author(self, pub_type):
        # ACCESS THE DRIVER WEB CHROME FIRST AND LOGIN
        driver = self.sinta_login()
        # ACCESS THE SCOPUS PROFILE WEB 
        url = f"https://sinta.kemdikbud.go.id/authors/profile/{self.ids}/?view={pub_type}"
        driver.get(url)
        print(self.ids)

        # GET THE PAGE TOTAL
        page_total = driver.find_element(By.XPATH, "//div[@class='profile-article']//nav[@aria-label='pagination-sample']//div[@class='text-center pagination-text']//small").text
        page_total = page_total.split()[3]
        page_total = page_total.replace('.', '')
        page_total = int(page_total)+1
        print(pub_type+": "+str(page_total))

        # GET ALL INFORMATIONS FOR EACH PAGES
        for page in range(1, page_total):
            full_url = f"https://sinta.kemdikbud.go.id/authors/profile/{self.ids}/?page={page}&view={pub_type}"
            # print(full_url)
            driver.get(full_url)
            driver.implicitly_wait(60)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "lxml")

            titles = soup.find_all("div", class_="ar-title")
            for title in titles:
                # print(title.find("a").text)
                # print(title.find("a")['href'])
                self.title.append(title.find("a").text)
                self.url.append(title.find("a")['href'])
                self.id_sinta.append(self.ids)
                self.pub_type.append(pub_type)
                self.uri.append(full_url)
            pubs = soup.find_all("a", class_="ar-pub")
            for pub in pubs:
                if "WOS.ESCI Edition" not in pub.text:
                    # print(pub.text)
                    self.pub.append(pub.text)
            quartiles = soup.find_all("a", class_="ar-quartile")
            for quartile in quartiles:
                # print(quartile.text)
                self.quartile.append(quartile.text)
            years = soup.find_all("a", class_="ar-year")
            for year in years:
                # print(year.text)
                self.year.append(year.text)
            citations = soup.find_all("a", class_="ar-cited")
            for cited in citations:
                # print(cited.text)
                self.cited.append(cited.text)
            
            articles = driver.find_elements(By.CLASS_NAME, "ar-list-item")

            if pub_type != "googlescholar":
                for article in articles:
                    armeta = article.find_elements(By.CSS_SELECTOR, ".ar-meta [href]")
                    # print(armeta[3].text)
                    self.creator.append(armeta[3].text)
            else:
                for article in articles:
                    armeta = article.find_elements(By.CSS_SELECTOR, ".ar-meta [href]")
                    # print(armeta[0].text)
                    self.creator.append(armeta[0].text)

        pre_processing = Preprocessing()
        df = pd.DataFrame.from_dict(data={'title': self.title, 'publication': self.pub, 'quartile / sinta': self.quartile, 'year': self.year, 'author': self.creator, 'cited': self.cited, 'url': self.url, 'uri': self.uri, 'type': self.pub_type, 'id_sinta': self.id_sinta}, orient='index').transpose()
        df['title'] = df['title'].apply(lambda x:pre_processing.clean_text(x))
        df['title'] = df['title'].apply(lambda x:x.lstrip())
        df['author'] = df["author"].str.replace("Creator : ", "")
        df['author'] = df["author"].str.replace("Authors : ", "")

        return df
    
    def sinta_univ(self):
        # ACCESS THE DRIVER WEB CHROME FIRST AND LOGIN
        driver = self.sinta_login()

        # GET THE PAGE TOTAL
        driver.get(f"https://sinta.kemdikbud.go.id/affiliations/profile/{self.ids}?page=1&view=scopus")
        page_total = driver.find_element(By.XPATH, "//div[@class='profile-article']//nav[@aria-label='pagination-sample']//div[@class='text-center pagination-text']//small").text
        page_total = page_total.split()[3]
        page_total = page_total.replace('.', '')

        # GET ALL INFORMATIONS FOR EACH PAGES
        for page in range(1, 3):
            driver.get(f"https://sinta.kemdikbud.go.id/affiliations/profile/{self.ids}?page={page}&view=scopus")
            articles = driver.find_elements(By.CLASS_NAME, "ar-list-item")

            for article in articles:
                self.title.append(article.find_element(By.CLASS_NAME, "ar-title").text)
                self.pub.append(article.find_element(By.CLASS_NAME, "ar-pub").text)
                self.year.append(article.find_element(By.CLASS_NAME, "ar-year").text)
                armeta = article.find_elements(By.CSS_SELECTOR, ".ar-meta [href]")
                self.creator.append(armeta[2].text)

        df = pd.DataFrame(data={'title': title, 'pub': pub, 'year': year, 'creator': creator})
        df['creator'] = df["creator"].str.split(": ", expand=True)[1]
        df.to_csv(f"data/data_crawling_sinta_univ_{today}.csv")
