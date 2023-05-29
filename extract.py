import pandas as pd
import numpy as np
from urllib.request import urlopen
import json
import re
from preprocessing import Preprocessing

def lppm(self):
    urls = ['http://repository.lppm.unila.ac.id/cgi/exportview/year/2023/JSON/2023.js', 'http://repository.lppm.unila.ac.id/cgi/exportview/year/1990/JSON/1990.js']
    dicts = {}
    df = pd.DataFrame()
    for url in urls:
        dict = urlopen(url).read()
        dict = json.loads(dict)
        data = pd.json_normalize(dict)
        df = pd.concat([df, data], ignore_index = True, axis = 0)
        print(df.info())

    columns = ['divisions', 'title', 'abstract', 'subjects', 'publication']
    pre_processing = Preprocessing()
    df[columns] = df[columns].replace(np.nan, '', regex=True)
    df[columns] = df[columns].applymap(lambda x:pre_processing.clean_text(x))
    print(df[columns])
    df[columns].to_csv("data_crawling.csv")