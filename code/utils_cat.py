"""
TODO
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import pymongo
import asyncio
import aiohttp
import time


def create_directory(path):
    """Create a directory at the specified path.

    If a file with the same name already exists at the specified path, a
    FileExistsError is raised and a message is printed.

    Parameters
    ----------
    path : str
        The path of the directory to be created.

    Returns
    -------
    None
        The function does not return anything. It only creates a directory or
        prints an error message if a file with the same name already exists
        at the specified path.
    """
    try:
        os.mkdir(path)
    except FileExistsError:
        print('File "data" exisits')


def clean_directories(path):
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
    data = requests.get(url, timeout=2.5, params=parameters)
    if data.ok:
        return data.json()
    return None


def get_information(url, parameters={}):
    data = requests.get(url, timeout=2.5, params=parameters)
    if data.ok:
        return data.json()
    return None


def save_json(path, data):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_csv(path, data):
    df = pd.DataFrame.from_dict(data, orient='index')
    df.to_csv(path, index=True)
    return None


def process_data(data):
    """
    Process a list of dictionaries containing meteorological observation data and return a list of processed dictionaries.
    
    Parameters
    ----------
    data : List[Dict[str, Any]]
        A list of dictionaries, where each dictionary contains meteorological observation data.
    
    Returns
    -------
    List[Dict[str, Union[str, float, datetime]]]
        A list of processed dictionaries, where each dictionary contains an observation ID, station ID, date, and a value
        for each meteorological variable.
    """
    sample_dict = dict((el, -1) for el in create_variables_dict('data/variables.json'))
    w_dict = {}
    w_list = []
    for obs in data:
        if len(obs['id']) == 14 and 'codi_estacio' in obs:
            if 'codi_estat' in obs:
                if obs['codi_estat'] == "V":
                    obs_id = obs['id'][:2] + obs['id'][4:]
                    var = obs['codi_variable']

                    if obs_id not in w_dict:
                        w_dict[obs_id] = sample_dict.copy()
                        w_dict[obs_id]['obs_id'] = obs_id
                        w_dict[obs_id]['station'] = obs['id'][:2]
                        w_dict[obs_id]['date'] = datetime.strptime(obs['data_lectura'], '%Y-%m-%dT%H:%M:%S.000')

                    w_dict[obs_id][var] = float(obs['valor_lectura'])
    
    for key in w_dict:
        w_list.append(w_dict[key])

    return w_list


def create_variables_dict(file_path):
    """
    Create a dictionary mapping variable codes to acronyms from a JSON file.
    
    Parameters
    ----------
    file_path : str
        The path to the JSON file containing the variable data. The file should contain a list of objects, with each object having a 'codi_variable' field and an 'acronim' field.
    
    Returns
    -------
    dict
        A dictionary with variable codes as keys and acronyms as values.
        
    Raises
    ------
    FileNotFoundError
        If the file does not exist at the specified file path.
    UnicodeDecodeError
        If the file cannot be read due to encoding issues.
    """
    v_dict = {}
    try:
        with open(file_path, encoding='UTF-8') as f:
            v_data = json.load(f)
            for var in v_data:
                v_dict[var['codi_variable']] = var['acronim']
    except (FileNotFoundError, UnicodeDecodeError) as e:
        print(f'Error reading file: {e}')
        return {}
    return v_dict


def getParams(ini_date):
    """
    Generate a list of dictionaries containing SQL WHERE clauses and LIMIT values for a given initial date.
    
    Parameters
    ----------
    ini_date : datetime
        The initial date in datetime format.
    
    Returns
    -------
    List[Dict[str, Union[str, int]]]
        A list of dictionaries, where each dictionary contains a WHERE clause specifying a date range and a LIMIT value.
    """
    last_date = datetime.today()
    dates = []
    while ini_date < last_date:
        end_date = ini_date + timedelta(days=1)
        where = f"data_lectura between '{ini_date.isoformat()}' and '{end_date.isoformat()}'"
        limit = 1000000
        dates.append({'$where': where, '$limit':limit})
        ini_date = end_date
    return dates

### DATABASE STUFF (TO BE CHANGED INTO ANOTHER .PY)
def connectDB(URI):
    """
    Connects to a MongoDB database and returns a client object.

    Parameters
    ----------
    URI : str
        The connection string for the MongoDB database.

    Returns
    -------
    Type[MongoClient]
        A client object for the specified MongoDB database.
    """
    client = pymongo.MongoClient(URI)
    return client['weather_cat']


def dbLastSample(db, collection):
    """
    Get the latest date from a collection in a MongoDB database.
    
    Parameters
    ----------
    db : pymongo.database.Database
        The MongoDB database.
    collection : str
        The name of the collection in the database.
    
    Returns
    -------
    datetime
        The latest date from the collection, or the default date (01/01/2009) if no documents are found or an error occurs.
    """
    default_date = datetime.strptime('01/01/2009', '%d/%m/%Y')
    try:
        latest_document = db[collection].find_one(sort=[('date', pymongo.DESCENDING)]).get('date')
        if latest_document != None:
            return latest_document
    except:
        return default_date


def dbInsertSamples(db, collection, data):
    """
    Inserts multiple documents into a collection in a MongoDB database and returns the number of inserted documents.

    Parameters
    ----------
    db : MongoClient
        A MongoDB client object.
    collection : str
        The name of the collection where the documents will be inserted.
    data : List[Dict[str, Any]]
        A list of dictionaries containing the documents to be inserted.

    Returns
    -------
    int
        The number of inserted documents.
    """
    if len(data) != 0:
        result = db[collection].insert_many(data)
        return len(result.inserted_ids)
    return 0


def dbQuery(db, collection, query):
    pass
