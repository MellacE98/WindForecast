import pandas as pd 
import json


def save_to_csv(df, file_name):
    df.to_csv(file_name, index=False)


def read_from_csv(file_name):
    return pd.read_csv(file_name)


def load_json(file_name):
    with open(file_name, encoding='UTF-8') as f:
        return json.load(f)
    
def save_json(file_name, data):
    with open(file_name, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_variables(file_path):
    v_list = []
    try:
        with open(file_path, encoding='UTF-8') as f:
            variables = f.readlines()
            for var in variables:
                v_list.append(var.strip())
    except (FileNotFoundError, UnicodeDecodeError) as e:
        print(f'Error reading file: {e}')
        return []
    
    return v_list


def get_station_info(file_path):
    s_dict = {}
    try:
        with open(file_path, encoding='UTF-8') as f:
            stations = json.load(f)
            for station in stations:
                s_dict[station['codi_estacio']] = {'station': station['codi_estacio'], 'altitud':station['altitud'], 'latitud':float(station['latitud']), 'longitud':float(station['longitud'])}
    except (FileNotFoundError, UnicodeDecodeError) as e:
        print(f'Error reading file: {e}')
        return {}
    
    return pd.DataFrame(s_dict).T
