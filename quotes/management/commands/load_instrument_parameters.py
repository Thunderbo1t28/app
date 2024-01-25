from django.core.management.base import BaseCommand
from quotes.models import Instrument, Quote
import requests
from datetime import datetime
import pandas as pd
from django.utils import timezone


MOEX_API_URL = "https://iss.moex.com/iss/engines/futures/markets/forts/securities.json"


class Command(BaseCommand):
    help = 'Load available instruments into the database'

    def handle(self, *args, **options):

        response = requests.get(MOEX_API_URL)
        if response.status_code == 200:
            data = response.json()
            
    
        else:
            print(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")
        
        # Предполагаем, что combined_df - это ваш DataFrame, а api_data - это ваш словарь данных
        # Это просто пример, и вам нужно адаптировать код к вашему случаю

        # Извлекаем данные из securities
        securities_data = data['securities']['data']
        
        securities_columns = data['securities']['columns']
        
        #columns=['SECID', 'BOARDID', 'SHORTNAME', 'SECNAME','PREVSETTLEPRICE', 'DECIMALS', 'MINSTEP',
        #'LASTTRADEDATE', 'LASTDELDATE', 'SECTYPE', 'LATNAME', 'ASSETCODE', 'PREVOPENPOSITION','LOTVOLUME',
        # 'INITIALMARGIN', 'HIGHLIMIT','LOWLIMIT', 'STEPPRICE', 'LASTSETTLEPRICE','PREVPRICE', 'IMTIME', 
        #'BUYSELLFEE','SCALPERFEE', 'NEGOTIATEDFEE', 'EXERCISEFEE'])
        # Создаем DataFrame из данных securities
        securities_df = pd.DataFrame(securities_data, columns=securities_columns)

        # Извлекаем данные из marketdata
        marketdata_data = data['marketdata']['data']
        marketdata_columns = data['marketdata']['columns']

        #"columns": ["SECID", "BOARDID", "BID", "OFFER", "SPREAD", "OPEN", "HIGH", "LOW", "LAST", "QUANTITY",
        # "LASTCHANGE", "SETTLEPRICE", "SETTLETOPREVSETTLE", "OPENPOSITION", "NUMTRADES", "VOLTODAY", "VALTODAY"
        #"VALTODAY_USD", "UPDATETIME", "LASTCHANGEPRCNT", "BIDDEPTH", "BIDDEPTHT", "NUMBIDS", "OFFERDEPTH"
        #"OFFERDEPTHT", "NUMOFFERS", "TIME", "SETTLETOPREVSETTLEPRC", "SEQNUM", "SYSTIME", "TRADEDATE", 
        #"LASTTOPREVPRICE", "OICHANGE", "OPENPERIODPRICE", "SWAPRATE"]

        # Создаем DataFrame из данных marketdata
        marketdata_df = pd.DataFrame(marketdata_data, columns=marketdata_columns)

        # Объединяем данные из обоих DataFrame по совпадающим столбцам (SECID, BOARDID)
        combined_df = pd.merge(securities_df, marketdata_df, how='inner', left_on=['SECID', 'BOARDID'], right_on=['SECID', 'BOARDID'])

        for row in combined_df.itertuples(index=False):
            
            existing_quotes = Instrument.objects.filter(
                instrument=row.ASSETCODE,
            )

            # Если данные уже существуют, пропускаем текущую итерацию цикла
            if existing_quotes.exists():
                continue

            

            Instrument.objects.create(
                instrument=row.ASSETCODE,
                description=row.SECNAME,
                point_size=row.LOTVOLUME,
                currency="RUB",
                asset_class="",
                slippage=row.MINSTEP,
                per_block=row.BUYSELLFEE,
                percentage=0.0,
                per_trade=0.0
            )
            print('Data loaded successfully')