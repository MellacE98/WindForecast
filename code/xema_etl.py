import asyncio
import etl_functions as etl
import time

async def etlMain(url):
    """TODO"""
    url_queue = asyncio.Queue()
    start = time.time()
    initial_date = etl.getLastDate('data/stations_data')
    
    print(f'Initial date found: {initial_date}')
    for api_params in etl.getParams(initial_date):
        url_queue.put_nowait(api_params)

    tasks = []
    for i in range(8):
        task = asyncio.create_task(etl.worker(f'worker_{i}', url_queue, 'data/stations_data', url, start))
        tasks.append(task)
    
    await url_queue.join()

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    print(f'DONE! Elapsed time: {time.time() - start:.2f}s')


async def etlDownloadMissing(url):
    """TODO"""
    url_queue = asyncio.Queue()
    start = time.time()

    missing = etl.getMissingDates('data/stations_data')
    print(f'Missing {len(missing)} dates')

    for api_params in etl.generateParams(missing):
        url_queue.put_nowait(api_params)

    tasks = []
    for i in range(8):
        task = asyncio.create_task(etl.worker(f'worker_{i}', url_queue, 'data/stations_data', url, start))
        tasks.append(task)
    
    await url_queue.join()

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    print(f'DONE! Elapsed time: {time.time() - start:.2f}s')
