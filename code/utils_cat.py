"""
TODO
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
import asyncio
import aiohttp
import time


def create_directory(path):
    """Creates a directory at path
    
    Keyword arguments:
    path -- path in which the directory will be created
    """
    print(path)
    try:
        os.mkdir(path)
    except FileExistsError:
        print('File "data" exisits')


def clean_directories(path):
    """Deletes files inside data directory
    
    path -- path of the directory to clean
    """
    for file in os.listdir(path):
        f_path = os.path.join(path, file)
        try:
            os.remove(path=f_path)
        except FileNotFoundError:
            continue

# https://dev.socrata.com/foundry/analisi.transparenciacatalunya.cat/nzvn-apee
# https://dev.socrata.com/docs/queries/
# https://dev.socrata.com/docs/datatypes/floating_timestamp.html#,

def get_information(url, parameters={}):
    """Requests information from a url

    Keyword arguments:
    url -- url to get the info
    parameters -- dict with the params for the request
    """
    data = requests.get(url, timeout=2.5, params=parameters)
    if data.ok:
        return data.json()
    return None


def get_information(url, parameters={}):
    """Requests information from a url

    Keyword arguments:
    url -- url to get the info
    parameters -- dict with the params for the request
    """
    data = requests.get(url, timeout=2.5, params=parameters)
    if data.ok:
        return data.json()
    return None


async def get(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            print("Successfully got url with resp of length {}.".format(len(resp)))
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


def save_json(path, data):
    """Saves .json file with the data

    Keyword arguments:
    path -- path in which the file will be saved
    data -- json format data to save into a .json
    """
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_csv(path, data):
    """Saves .csv file with the data

    Keyword arguments:
    path -- path in which the file will be saved
    data -- dict with data to save into a .csv
    """
    df = pd.DataFrame.from_dict(data, orient='index')
    df.to_csv(path, index=True)
    return None


def process_data(path, data):
    """
    TODO
    """
    sample_dict = dict((el, -1) for el in create_variables_dict())
    w_dict = {}
    for obs in data:
        obs_id = obs['id'][:2] + obs['id'][4:]
        variable = obs['codi_variable']
        if obs_id not in w_dict:
            w_dict[obs_id] = sample_dict.copy()
        w_dict[obs_id][variable] = obs['valor_lectura']
    return w_dict


def create_variables_dict():
    """Returns a dict where variable codes are keys and acronims the values"""
    v_dict = {}
    v_data = json.load(open('data/variables.json', encoding='UTF-8'))
    for var in v_data:
        v_dict[var['codi_variable']] = var['acronim']
    return v_dict


def getParams(url, ini_date):
    last_date = datetime.strptime('30/01/2009', '%d/%m/%Y')
    ini_date = datetime.strptime(ini_date, '%d/%m/%Y')
    dates = []
    while ini_date < last_date:
        end_date = ini_date + timedelta(days=1)
        where = f"data_lectura between '{ini_date.isoformat()}' and '{end_date.isoformat()}'"
        limit = 1000000
        dates.append(url+f'?$limit={limit}&$where={where}')
        ini_date = end_date
    return dates


def connectDB(URI):
    client = MongoClient(URI)
    print('success')
    client.close()