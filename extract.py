import pandas as pd
import numpy as np
import time
import json
import os
from dotenv import load_dotenv
from urllib.request import urlopen
from datetime import date
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from preprocessing import Preprocessing

today = date.today()

def webdriver_config():
    # initiate and call the browser for scraping
    # set the header
    # ua = UserAgent(verify_ssl=False)
    ua = UserAgent()
    userAgent = ua.random
    header = {'User-Agent': userAgent}
    # set the browser option 
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
    # create list year for url
    list_year = ['3276', '3018', '2107', '1985', '1977', '1010', '0223', '0220', '0214', '0207', '0202', '0201', '0200', '0029', '0028', '0022', '0021', '0020', '0017', '0016', '0015']
    for i in range(1990, 2025):
        list_year.append(str(i))
    list_year = sorted(list_year, reverse=True)
    # print(len(list_year))
    # urls = ['http://repository.lppm.unila.ac.id/cgi/exportview/year/2023/JSON/2023.js', 'http://repository.lppm.unila.ac.id/cgi/exportview/year/1990/JSON/1990.js']
    urls = list_year

    # collect data from each url
    df = pd.DataFrame()
    for idx, url in enumerate(urls):
        url = f'http://repository.lppm.unila.ac.id/cgi/exportview/year/{url}/JSON/{url}.js'
        # print(url)
        dict = urlopen(url).read()
        dict = json.loads(dict)
        data = pd.json_normalize(dict)
        print(f"data {idx}: {len(data)}")
        df = pd.concat([df, data], ignore_index = True, axis = 0)

    # clean data collection and convert into csv
    columns = ['divisions', 'title', 'abstract', 'subjects', 'publication']
    pre_processing = Preprocessing()
    df[columns] = df[columns].replace(np.nan, '', regex=True)
    df[columns] = df[columns].applymap(lambda x:pre_processing.clean_text(x))
    print("Total data:", len(df[columns]))
    df[columns].to_csv(f"data/data_crawling_lppmunila_year_{today}.csv")

def gscholar_idauthor():
    # initiate and call the browser for scraping
    # set the header
    # ua = UserAgent(verify_ssl=False)
    ua = UserAgent()
    userAgent = ua.random
    header = {'User-Agent': userAgent}
    # set the browser option 
    chrome_options = Options()
    chrome_options.headless = True # comment this line to see the browser running
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--log-level=1")
    chrome_options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    # access article link from authors
    # list_idgs = ['sXyP1GYAAAAJ', 'SdfFZQYAAAAJ', 'x3ceWPkAAAAJ']
    list_idgs = ['sXyP1GYAAAAJ']
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

        # crawling information from each article link into dictionary, list, and json later
        df = pd.DataFrame()
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

def gscholar_idauthor_telegrambot():
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'} 
    
    idgs = 'sXyP1GYAAAAJ'
    url_author = f"https://scholar.google.com/citations?user={idgs}"
    response = requests.get(url_author, headers=header)
    soup = BeautifulSoup(response.content, 'lxml')
    url_articles = []
    for a in soup.find_all('a', class_="gsc_a_at"):
        link_article = f"https://scholar.google.com/{a['href']}"
        # print(link_article)
        url_articles.append(link_article)
    print("Total articles: ", len(url_articles))

    # crawling information from each article link into dictionary, list, and json later
    articles = []
    df = pd.DataFrame()
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

def sinta_univ():
    load_dotenv()

    USERNAME_SINTA = os.getenv("USERNAME_SINTA")
    PASSWORD_SINTA = os.getenv("PASSWORD_SINTA")
    ID_AFF_PROFIL = os.getenv("ID_AFF_SINTA")

    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()

    driver.get("https://sinta.kemdikbud.go.id/logins")

    username = driver.find_element(By.NAME, "username")
    username.send_keys(USERNAME_SINTA)

    password = driver.find_element(By.NAME, "password")
    password.send_keys(PASSWORD_SINTA)

    submit = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit.click()

    driver.implicitly_wait(30)

    title = []
    pub = []
    year = []
    creator = []

    # get page total
    driver.get(f"https://sinta.kemdikbud.go.id/affiliations/profile/{ID_AFF_PROFIL}?page=1&view=scopus")
    page_total = driver.find_element(By.XPATH, "//div[@class='profile-article']//nav[@aria-label='pagination-sample']//div[@class='text-center pagination-text']//small").text
    page_total = page_total.split()[3]
    page_total = page_total.replace('.', '')

    # get all informations for each pages
    for page in range(1, 3):
        driver.get(f"https://sinta.kemdikbud.go.id/affiliations/profile/{ID_AFF_PROFIL}?page={page}&view=scopus")
        articles = driver.find_elements(By.CLASS_NAME, "ar-list-item")

        for article in articles:
            title.append(article.find_element(By.CLASS_NAME, "ar-title").text)
            pub.append(article.find_element(By.CLASS_NAME, "ar-pub").text)
            year.append(article.find_element(By.CLASS_NAME, "ar-year").text)
            armeta = article.find_elements(By.CSS_SELECTOR, ".ar-meta [href]")
            creator.append(armeta[2].text)

    df = pd.DataFrame(data={'title': title, 'pub': pub, 'year': year, 'creator': creator})
    df['creator'] = df["creator"].str.split(": ", expand=True)[1]
    df.to_csv(f"data/data_crawling_sinta_univ_{today}.csv")

def sinta_author():
    load_dotenv()

    USERNAME_SINTA = os.getenv("USERNAME_SINTA")
    PASSWORD_SINTA = os.getenv("PASSWORD_SINTA")

    chrome_options = webdriver_config()
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    ID_PROFIL = os.getenv("ID_PROFILE_SINTA")
    url = f"https://sinta.kemdikbud.go.id/authors/profile/{ID_PROFIL}"

    # set config
    driver = webdriver.Chrome(options=chrome_options)

    # login first to sinta
    driver.get("https://sinta.kemdikbud.go.id/logins")
    username = driver.find_element(By.NAME, "username")
    username.send_keys(USERNAME_SINTA)
    password = driver.find_element(By.NAME, "password")
    password.send_keys(PASSWORD_SINTA)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
    # time.sleep(5)

    # set the list
    title = []
    pub = []
    year = []
    quartile = []
    cited = []
    creator = []
    pub_type = []

    # access the author url, specifically for the scopus
    view = "scopus"
    driver.get(url+"?view="+view)
    # driver.implicitly_wait(60)
    # time.sleep(5)

    # get page total
    page_total = driver.find_element(By.XPATH, "//div[@class='profile-article']//nav[@aria-label='pagination-sample']//div[@class='text-center pagination-text']//small").text
    page_total = page_total.split()[3]
    page_total = page_total.replace('.', '')
    page_total = int(page_total)+1
    print(view+": "+str(page_total))

    # get all informations for each pages
    for page in range(1, page_total):
        full_url = f"{url}/?page={page}&view={view}"
        print(full_url)
        driver.get(full_url)
        # driver.implicitly_wait(60)
        # time.sleep(5)

        # page = requests.get(full_url)
        # soup = BeautifulSoup(page.content, "html.parser")
        # titles = soup.find_all("div", class_="ar-title")
        # print(len(titles))
        # for title in titles:
        #     title_element = title.find("a").text
        #     print(title_element)
        # time.sleep(5)

        articles = driver.find_elements(By.CLASS_NAME, "ar-list-item")
        
        for article in articles:
            title.append(article.find_element(By.CLASS_NAME, "ar-title").text)
            # print(article.find_element(By.CLASS_NAME, "ar-title").text)
            pub.append(article.find_element(By.CLASS_NAME, "ar-pub").text)
            quartile.append(article.find_element(By.CLASS_NAME, "ar-quartile").text)
            year.append(article.find_element(By.CLASS_NAME, "ar-year").text)
            cited.append(article.find_element(By.CLASS_NAME, "ar-cited").text)
            armeta = article.find_elements(By.CSS_SELECTOR, ".ar-meta [href]")
            creator.append(armeta[3].text)
            pub_type.append(view)

    # access the author url, specifically for the web of science
    view = "wos"
    driver.get(url+"?view="+view)
    # driver.implicitly_wait(60)
    # time.sleep(5)

    # get page total
    page_total = driver.find_element(By.XPATH, "//div[@class='profile-article']//nav[@aria-label='pagination-sample']//div[@class='text-center pagination-text']//small").text
    page_total = page_total.split()[3]
    page_total = page_total.replace('.', '')
    page_total = int(page_total)+1
    print(view+": "+str(page_total))

    # get all informations for each pages
    for page in range(1, page_total):
        full_url = f"{url}/?page={page}&view={view}"
        print(full_url)
        driver.get(full_url)
        # driver.implicitly_wait(60)
        # time.sleep(5)

        articles = driver.find_elements(By.CLASS_NAME, "ar-list-item")

        for article in articles:
            title.append(article.find_element(By.CLASS_NAME, "ar-title").text)
            pub.append(article.find_element(By.CLASS_NAME, "ar-pub").text)
            quartile.append(article.find_element(By.CLASS_NAME, "ar-quartile").text)
            year.append(article.find_element(By.CLASS_NAME, "ar-year").text)
            cited.append(article.find_element(By.CLASS_NAME, "ar-cited").text)
            armeta = article.find_elements(By.CSS_SELECTOR, ".ar-meta [href]")
            creator.append(armeta[3].text)
            pub_type.append(view)

    # access the author url, specifically for the garuda
    view = "garuda"
    driver.get(url+"?view="+view)
    # driver.implicitly_wait(60)
    # time.sleep(5)

    # get page total
    page_total = driver.find_element(By.XPATH, "//div[@class='profile-article']//nav[@aria-label='pagination-sample']//div[@class='text-center pagination-text']//small").text
    page_total = page_total.split()[3]
    page_total = page_total.replace('.', '')
    page_total = int(page_total)+1
    print(view+": "+str(page_total))

    # get all informations for each pages
    for page in range(1, page_total):
        full_url = f"{url}/?page={page}&view={view}"
        print(full_url)
        driver.get(full_url)
        # driver.implicitly_wait(60)
        # time.sleep(5)

        articles = driver.find_elements(By.CLASS_NAME, "ar-list-item")

        for article in articles:
            title.append(article.find_element(By.CLASS_NAME, "ar-title").text)
            pub.append(article.find_element(By.CLASS_NAME, "ar-pub").text)
            quartile.append(article.find_element(By.CLASS_NAME, "ar-quartile").text)
            year.append(article.find_element(By.CLASS_NAME, "ar-year").text)
            cited.append(article.find_element(By.CLASS_NAME, "ar-cited").text)
            armeta = article.find_elements(By.CSS_SELECTOR, ".ar-meta [href]")
            creator.append(armeta[3].text)
            pub_type.append(view)

    # access the author url, specifically for the google scholar
    view = "googlescholar"
    driver.get(url+"?view="+view)
    # driver.implicitly_wait(60)
    # time.sleep(5)

    # get page total
    page_total = driver.find_element(By.XPATH, "//div[@class='profile-article']//nav[@aria-label='pagination-sample']//div[@class='text-center pagination-text']//small").text
    page_total = page_total.split()[3]
    page_total = page_total.replace('.', '')
    page_total = int(page_total)+1
    print(view+": "+str(page_total))

    # get all informations for each pages
    for page in range(1, page_total):
        full_url = f"{url}/?page={page}&view={view}"
        print(full_url)
        driver.get(full_url)
        # driver.implicitly_wait(60)
        # time.sleep(5)
        
        articles = driver.find_elements(By.CLASS_NAME, "ar-list-item")

        for article in articles:
            title.append(article.find_element(By.CLASS_NAME, "ar-title").text)
            pub.append(article.find_element(By.CLASS_NAME, "ar-pub").text)
            quartile.append("")
            year.append(article.find_element(By.CLASS_NAME, "ar-year").text)
            cited.append(article.find_element(By.CLASS_NAME, "ar-cited").text)
            armeta = article.find_elements(By.CSS_SELECTOR, ".ar-meta [href]")
            creator.append(armeta[0].text)
            pub_type.append(view)

    df = pd.DataFrame(data={'title': title, 'publication': pub, 'quartile / sinta': quartile, 'year': year, 'cited': cited, 'author': creator, 'type': pub_type})
    df['author'] = df["author"].str.replace("Creator : ", "")
    df['author'] = df["author"].str.replace("Authors : ", "")

    df.to_csv(f"data/data_crawling_sinta_author_{today}.csv", index=False)


# if __name__ == "__main__":
#     gscholar_idauthor()

