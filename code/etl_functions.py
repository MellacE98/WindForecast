import json
import aiohttp
import time
import os
import pandas as pd
from datetime import datetime, timedelta
import utils
import math


WANTED_VARIABLES = utils.get_variables('data/wanted.txt')
STATION_INFO = utils.get_station_info('data/stations.json')


def getMissingDates(path):
    """TODO"""
    files = os.listdir(path)
    name_list = [file.strip('.csv') for file in files[1:-1]]
    supposed_list = []

    start_date = pd.to_datetime(files[0], format='%Y%m%d.csv')
    end_date = pd.to_datetime(files[-1], format='%Y%m%d.csv')

    while start_date < end_date:
        start_date += pd.Timedelta(days=1)
        supposed_list.append(start_date.strftime('%Y%m%d'))

    missing_dates = set(supposed_list) - set(name_list)
    return list(missing_dates)


def getLastDate(path):
    """TODO"""
    files = os.listdir(path)
    if len(files) == 0:
        return datetime(2009, 1, 1)

    last_file = files[-1]
    last_date = datetime.strptime(last_file, '%Y%m%d.csv')
    return last_date


def generateParams(values):
    """TODO"""
    dates = []
    for val in values:
        ini_date = datetime.strptime(val, '%Y%m%d')
        end_date = ini_date + timedelta(days=1)
        where = f"data_lectura between '{ini_date.isoformat()}' and '{end_date.isoformat()}'"
        limit = 1000000
        dates.append({'$where': where, '$limit':limit})
    return dates


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
        end_date = ini_date + timedelta(hours=23, minutes=50)
        where = f"data_lectura between '{ini_date.isoformat()}' and '{end_date.isoformat()}'"
        limit = 1000000
        dates.append({'$where': where, '$limit':limit})
        ini_date = ini_date + timedelta(days=1)
    return dates


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
        if obs['codi_variable'] in WANTED_VARIABLES and len(obs['id']) == 14 and 'codi_estacio' in obs:
            if 'codi_estat' in obs:
                obs_id = obs['id'][:2] + obs['id'][4:]
                var = obs['codi_variable']

                if obs_id not in w_dict:
                    w_dict[obs_id] = sample_dict.copy()
                    
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


def convert_data(data):
    """
    Convert a list of dictionaries to a pandas DataFrame.
    
    Parameters
    ----------
    data : List[Dict[str, Any]]
        A list of dictionaries, where each dictionary contains meteorological observation data.
    
    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the data from the input list of dictionaries.
    """
    df = pd.DataFrame(data)

    if len(df) == 0:
        return df, -1
    
    df = df[WANTED_VARIABLES+['station', 'date']]

    df['u2'], df['v2'] = [-1, -1]
    df['u6'], df['v6'] = [-1, -1]
    df['u10'], df['v10'] = [-1, -1]

    df.loc[df['46'] != -1, 'u2'] = round(df.loc[df['46'] != -1, '46'] * df.loc[df['46'] != -1, '47'].apply(math.cos), 1)
    df.loc[df['46'] != -1, 'v2'] = round(df.loc[df['46'] != -1, '46'] * df.loc[df['46'] != -1, '47'].apply(math.sin), 1)

    df.loc[df['48'] != -1, 'u6'] = round(df.loc[df['48'] != -1, '48'] * df.loc[df['48'] != -1, '49'].apply(math.cos), 1)
    df.loc[df['48'] != -1, 'v6'] = round(df.loc[df['48'] != -1, '48'] * df.loc[df['48'] != -1, '49'].apply(math.sin), 1)

    df.loc[df['30'] != -1, 'u10'] = round(df.loc[df['30'] != -1, '30'] * df.loc[df['30'] != -1, '31'].apply(math.cos), 1)
    df.loc[df['30'] != -1, 'v10'] = round(df.loc[df['30'] != -1, '30'] * df.loc[df['30'] != -1, '31'].apply(math.sin), 1)

    df = pd.merge(df, STATION_INFO, on='station', how='left')

    df['date'] = pd.to_datetime(df['date'])

    df.reset_index(drop=True, inplace=True)
    try:
        df = df.drop(columns=['46', '47', '48', '49', '30', '31'])
        df.rename({'32': 'T', '33': 'HR', '34':'P'}, axis='columns', inplace=True)
        return df, 0
    except KeyError:
        return df, -1


async def worker(name, queue, path, url, start_time, print_interval=10):
    async with aiohttp.ClientSession() as session:
        last_print_time = time.time()
        while not queue.empty():
            params = await queue.get()
            try:
                async with session.get(url=url, params=params) as response:
                    if response.ok:
                        json_response = await response.json()
                        data_dict = process_data(json_response)
                        df, result = convert_data(data_dict)
                        if result == -1:
                            continue
                        file_name = f'{path}/{df["date"][0].strftime("%Y%m%d")}.csv'
                        utils.save_to_csv(df, file_name)
            except Exception as e:
                print(f"Unable to get {params} due to {e.__class__}")
            finally:
                queue.task_done()

            elapsed_time = time.time() - start_time
            if time.time() - last_print_time >= print_interval:
                print(f'{queue.qsize()} items left. Elapsed time {elapsed_time:.2f}s', end='\r')
                last_print_time = time.time()

        print(f'{queue.qsize()} items left. Elapsed time {elapsed_time:.2f}s')