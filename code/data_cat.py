"""
TODO
"""

import etl
import os
import asyncio
import aiohttp
import time

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

VARIABLES_URL = 'https://analisi.transparenciacatalunya.cat/resource/4fb2-n3yi.json'
STATIONS_URL = 'https://analisi.transparenciacatalunya.cat/resource/yqwd-vj5e.json'
DATA_URL = 'https://analisi.transparenciacatalunya.cat/resource/nzvn-apee.json'

async def main():
    await etl.main_etl(DATA_URL)
    return 0

if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    end = time.time()

    print(f"Took {end- start:.2f} seconds to pull websites.")
