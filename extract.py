import pandas as pd
import numpy as np
from urllib.request import urlopen
import json
from preprocessing import Preprocessing
from datetime import date

def lppm():
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
    today = date.today()
    df[columns].to_csv(f"data/data_crawling_{today}.csv")

if __name__ == "__main__":
    lppm()