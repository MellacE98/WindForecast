"""
TODO
"""

import etl
import os

VARIABLES_URL = 'https://analisi.transparenciacatalunya.cat/resource/4fb2-n3yi.json'
STATIONS_URL = 'https://analisi.transparenciacatalunya.cat/resource/yqwd-vj5e.json'
DATA_URL = 'https://analisi.transparenciacatalunya.cat/resource/nzvn-apee.json'

def main():
    """
    TODO
    
    path = os.getcwd()
    print(path)
    json_data = utils_cat.get_information(STATIONS_URL)
    utils_cat.save_json(os.path.join(path, 'data', 'stations.json'), json_data)

    json_data = utils_cat.get_information(VARIABLES_URL)
    utils_cat.save_json(os.path.join(path, 'data', 'variables.json'), json_data)
    
    json_data = utils_cat.get_information(DATA_URL, {'$limit': 10000000}) #"data_lectura between '2015-01-10T12:00:00' and '2017-01-10T14:00:00'"
    utils_cat.save_json(os.path.join(path, 'data', 'prueba.json'), json_data)

    dict_data = utils_cat.process_data(os.path.join(path, 'data', 'prueba.csv'), json_data)    
    utils_cat.save_csv(os.path.join(path, 'data', 'prueba.csv'), dict_data)
    """
    #etl.extract(DATA_URL)
    etl.load()
    return 0

if __name__ == '__main__':
    main()
