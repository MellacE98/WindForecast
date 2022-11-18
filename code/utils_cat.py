"""
TODO
"""

import json
import requests
import pandas as pd

def get_variables():
    """
    TODO
    """
    url = 'https://analisi.transparenciacatalunya.cat/resource/4fb2-n3yi.json'
    variables = requests.get(url, timeout=2.5)
    if variables.ok:
        with open('data/variables.json', 'w', encoding='UTF-8') as file:
            json.dump(variables.json(), file)
        return 1
    return 0


def get_station():
    """
    TODO
    """
    url = 'https://analisi.transparenciacatalunya.cat/resource/yqwd-vj5e.json'
    stations = requests.get(url, timeout=2.5)
    if stations.ok:
        with open('data/stations.json', 'w', encoding='UTF-8') as file:
            json.dump(stations.json(), file)
        return 1
    return 0


def get_values():
    """
    TODO
    """
    sample_dict = dict((el, -1) for el in create_variables_dict())
    w_dict = {}
    limit, offset = 10000, 0
    url = 'https://analisi.transparenciacatalunya.cat/resource/nzvn-apee.json'

    weather = requests.get(url, timeout=2.5, params={'$offset': offset, '$limit': limit})
    if weather.ok:
        data = weather.json()
        for obs in data:
            id = obs['id'][:2] + obs['id'][4:]
            variable = obs['codi_variable']
            if id not in w_dict:
                w_dict[id] = sample_dict.copy()
                w_dict[id][variable] = obs['valor_lectura']
        return pd.DataFrame(w_dict.items())
    else:
        return 0


def create_variables_dict():
    """
    TODO
    """
    v_dict = {}
    v_data = json.load(open('data/variables.json', encoding='UTF-8'))
    for var in v_data:
        v_dict[var['codi_variable']] = var['acronim']
    return v_dict
