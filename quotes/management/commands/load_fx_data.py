import time
from django.core.management.base import BaseCommand
from django.utils import timezone
import pandas as pd
import requests
from datetime import datetime, timedelta
from quotes.models import FxPriceData

class Command(BaseCommand):
    help = 'Load available instruments into the database'
    
    
    def handle(self, *args, **options):
        # Базовый URL
        base_url = "https://iss.moex.com/iss/history/engines/currency/markets/index/securities.json"
        fx_name = {'BYNFIXME': 'BYNRUB',
               'CNYFIX': 'СNYRUB', 'EURFIX': 'EURRUB',
               'EURUSDFIX': 'EURUSD', 'USDFIX': 'USDRUB'}
        # Получаем текущую дату
        current_date =  datetime.strptime("2020-01-01", "%Y-%m-%d").date()  #datetime.now().date()

        # Задаем конечную дату (например, "2024-01-01")
        end_date = datetime.strptime("2010-01-01", "%Y-%m-%d").date()
        
        # Инициализируем список дат, начиная от текущей и идя к заданной конечной дате
        date_list = []
        while current_date >= end_date:
            date_list.append(current_date)
            current_date -= timedelta(days=1)



        for query_date in date_list:
            formatted_date = query_date.strftime("%Y-%m-%d")
            full_url = f"{base_url}?date={formatted_date}"
            # Выполняем HTTP-запрос
            response = requests.get(full_url)
            response_data = response.json()['history']['data']
            response_columns = response.json()['history']['columns']
            response_df = pd.DataFrame(response_data, columns=response_columns)
            # Обрабатываем данные и добавляем в базу данных
            quotes_to_create = []

            for item in response_df.itertuples(index=False):
                # Ваш код обработки данных
                sec_id = item.SECID
                if sec_id and sec_id in fx_name:
                    currency = fx_name[sec_id]
                    # Проверка наличия данных
                    if pd.notna(item.TRADEDATE) and pd.notna(item.CLOSE):
                        existing_quotes = FxPriceData.objects.filter(
                            instrument=sec_id,
                            timestamp=item.TRADEDATE
                        )

                        # Если данные уже существуют, пропускаем текущую итерацию цикла
                        if existing_quotes.exists():
                            continue
                        
                            
                        quote_data = {
                            'timestamp': item.TRADEDATE,
                            'exchange': 'MOEX',
                            'instrument': sec_id,
                            'currency': currency,
                            'section': item.BOARDID,
                            'price': item.CLOSE
                        }
                        quotes_to_create.append(FxPriceData(**quote_data))
                        #print(f'Data loaded successfully   {instrument}  {contract}  {item.TRADEDATE}')
                    

            if quotes_to_create:
                FxPriceData.objects.bulk_create(quotes_to_create)
                print(len(quotes_to_create))
            

            #time.sleep(1)