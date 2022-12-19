"""
TODO
"""


import asyncio
import aiohttp
import time
import os
import pandas as pd
from datetime import datetime, timedelta
import utils_cat

path = os.getcwd()

async def worker(name, queue, db, url):
    async with aiohttp.ClientSession() as session:
        counter = 0
        while True:
            params = await queue.get()

            try:
                async with session.get(url=url, params=params) as response:
                    json_response = await response.json()
                    data_dict = utils_cat.process_data(json_response)
                    utils_cat.dbInsertSamples(db, 'observations', data_dict)
  
            except Exception as e:
                print(e.details)
                print(f"Unable to get {url} due to {e.__class__}")

            
            print(f'Worker {name} finished task {counter}')
            counter += 1
            queue.task_done()


async def main_etl(url):
    """
    TODO
    """
    # Create the api url queue to get information from
    url_queue = asyncio.Queue()

    db = utils_cat.connectDB('mongodb://localhost:27017')
    ### LLAMAR FUNCION QUE PILLA DE LA BD EL ULTIMO DIA MEDIDO, de momento 01/01/2009
    ini_date = utils_cat.dbLastSample(db, 'observations')
    print(f'Initial date found: {ini_date}')
    for api_params in utils_cat.getParams(ini_date):
        url_queue.put_nowait(api_params)

    # Workers that will visit the urls and fetch the data
    tasks = []
    for i in range(8):
        task = asyncio.create_task(worker(f'worker_{i}', url_queue, db, url))
        tasks.append(task)

    # Wait for the urls to be processed
    start = time.monotonic()
    await url_queue.join()
    total_time = time.monotonic() - start

    # Cancel worker tasks
    for task in tasks:
        task.cancel()
    
    # Wait for all the tasks to end and be cancelled
    await asyncio.gather(*tasks, return_exceptions=True)



