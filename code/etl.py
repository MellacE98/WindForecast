"""
TODO
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import utils_cat

path = os.getcwd()

def extract(url, ini_date='01/01/2009'):
    last_day = datetime.today()
    if ini_date=='01/01/2009':
        ini_date = datetime.strptime(ini_date, '%d/%m/%Y')
    end_date = ini_date + timedelta(days=1)
    if end_date > last_day:
        print("Data is up to date")
        return 1
    parameters = {
        '$where': f"data_lectura between '{ini_date.isoformat()}' and '{end_date.isoformat()}'",
        '$limit': 1000000
        } 
    json_data = utils_cat.get_information(url, parameters)
    utils_cat.save_json(os.path.join(path, 'data', 'prueba.json'), json_data)
    return end_date


def transform():
    pass


def load():
    utils_cat.connectDB('mongodb://localhost:27017')
    
