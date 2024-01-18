from django.core.management.base import BaseCommand
from quotes.models import Quote
import requests
from datetime import datetime
import pandas as pd
from django.utils import timezone

instrument_to_format = {
    'AE': 'AE_%Y%m%d',
    # Добавьте другие инструменты, если необходимо
}

contracts_to_instruments = {
        'AE_20240300': 'AED',
        
        # и так далее
        }

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

        # Выводим первые строки объединенного DataFrame
        
        #print(combined_df.head())

        
        for row in combined_df.itertuples(index=False):
            
            
            date_time_str = timezone.make_aware(datetime.strptime(row.IMTIME, "%Y-%m-%d %H:%M:%S")) if row.IMTIME is not None else None
            
            

            # Преобразование объекта datetime обратно в строку с новым форматом
            date_str = date_time_str.strftime("%Y-%m-%d") 
            sec_id = row.SECID
            #print(sec_id)
            sectype = sec_id[:-2]
            #last_two_chars = sec_id[-2:]
            #print(sectype)
            #cleaned_string = ''.join(filter(str.isdigit, last_two_chars[1]))
            if len(sectype)==2:
                #year_digit = int(cleaned_string)
                #month_char = last_two_chars[0]
                #month_mapping = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6, 'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}
                #month = month_mapping.get(month_char, None)
                last_trade_date = datetime.strptime(row.LASTTRADEDATE, "%Y-%m-%d").strftime("%Y%m%d")
                #contract_date = last_trade_date[:-5]
                #contract_time = f'{contract_date}{year_digit:d}{month:02d}00'
                contract = f'{sectype}_{last_trade_date}'
                if pd.notna(row.TRADEDATE) and pd.notna(row.OPEN) and pd.notna(row.LOW) and pd.notna(row.HIGH) and pd.notna(row.PREVPRICE) and pd.notna(row.VOLTODAY):
                    existing_quotes = Quote.objects.filter(
                        instrument=row.ASSETCODE,
                        contract=contract,
                        timestamp=date_str
                    )

                    # Если данные уже существуют, пропускаем текущую итерацию цикла
                    if existing_quotes.exists():
                        continue

                    

                    Quote.objects.create(
                        exchange='MOEX',
                        instrument=row.ASSETCODE,
                        section=row.BOARDID,
                        contract=contract,
                        sectype=row.SECTYPE,
                        secid=row.SECID,
                        open_price=row.OPEN,
                        low_price=row.LOW,
                        high_price=row.HIGH,
                        close_price=row.PREVPRICE,
                        volume=row.VOLTODAY,
                        timestamp=date_str
                    )
                    print('Data loaded successfully')
            else:
                if pd.notna(row.TRADEDATE) and pd.notna(row.OPEN) and pd.notna(row.LOW) and pd.notna(row.HIGH) and pd.notna(row.PREVPRICE) and pd.notna(row.VOLTODAY):

                    existing_quotes = Quote.objects.filter(
                        instrument=row.ASSETCODE,
                        contract=contract,
                        timestamp=date_str
                    )

                    # Если данные уже существуют, пропускаем текущую итерацию цикла
                    if existing_quotes.exists():
                        continue

                    

                    Quote.objects.create(
                        exchange='MOEX',
                        instrument=row.ASSETCODE,
                        section=row.BOARDID,
                        contract=row.SECID,
                        sectype=row.SECTYPE,
                        secid=row.SECID,
                        open_price=row.OPEN,
                        low_price=row.LOW,
                        high_price=row.HIGH,
                        close_price=row.PREVPRICE,
                        volume=row.VOLTODAY,
                        timestamp=date_str
                    )
                    print('Data loaded successfully')