import argparse
from xema_etl import etlMain, etlDownloadMissing
import asyncio

DATA_URL = 'https://analisi.transparenciacatalunya.cat/resource/nzvn-apee.json'

async def main():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    parser = argparse.ArgumentParser(description= 'Program to fetch data and train a model to predict the weather in Catalonia.' )

    parser.add_argument( '--update', action='store_true', help='Check last download date and update the data' )
    parser.add_argument( '--train', nargs=3, help= 'Train the model with data of specified date and time window' )

    args = parser.parse_args()

    if args.update:
        print( 'Updating data...' )
        await etlMain(DATA_URL)
        await etlDownloadMissing(DATA_URL)
        print( 'Data updated.' )

    if args.train:
        print( 'Training model...' )
        # TODO



if __name__ ==  '__main__':
    asyncio.run(main())