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

async def worker(name, queue):
    while True:
        url = await queue.get()

        # Visit the url
        await asyncio.sleep(3)

        # The item has been processed
        queue.task_done()

    pass


async def main_etl(url):
    """
    TODO
    """
    # Create the url queue to get information from
    url_queue = asyncio.Queue()

    ### LLAMAR FUNCION QUE PILLA DE LA BD EL ULTIMO DIA MEDIDO, de momento 01/01/2009
    ini_date = '01/01/2009'

    for api_url in utils_cat.getParams(url, ini_date):
        url_queue.put_nowait(api_url)

    print(f'Workers initial sleep time {url_queue.qsize()*3:.2f} seconds')
    # Workers that will visit the urls and fetch the data
    tasks = []
    for i in range(32):
        task = asyncio.create_task(worker(f'worker_{i}', url_queue))
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

    print(f'Workers visited fetched the information for {total_time:.2f} seconds')
    print(url_queue.qsize())


