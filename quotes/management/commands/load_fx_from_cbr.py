from django.core.management.base import BaseCommand, CommandError
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysinit.futures.adjustedprices_from_mongo_multiple_to_mongo import process_adjusted_prices_all_instruments
from sysinit.futures.contract_prices_from_csv_to_arctic import init_arctic_with_csv_futures_contract_prices
from sysinit.futures.multipleprices_from_arcticprices_and_csv_calendars_to_arctic import process_multiple_prices_all_instruments
import json
import os
import logging
import time
#from django.utils import timezone
import pandas as pd
import requests
from datetime import datetime, timedelta
from quotes.models import Instrument, LastDownloadDate, Quote
from django.db.models import Max
import xml.etree.ElementTree as ET
from quotes.models import FxPriceData
from sysinit.futures.spotfx_from_csvAndInvestingDotCom_to_arctic import spotfx_from_csv_and_investing_dot_com


# Настройка логирования
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load data to database'

      

    def handle(self, *args, **options):
        # Отладочное логирование для проверки аргументов
        try:
            base_url = "https://cbr.ru/scripts/XML_daily_eng.asp"
            fx_name = {
                                    'AUD' : 'AUDRUB',
                                    'AZN' : 'AZNRUB',
                                    'GBP' : 'GBPRUB',
                                    'AMD' : 'AMDRUB',
                                    'BYN' : 'BYNRUB',
                                    'BGN' : 'BGNRUB',
                                    'BRL' : 'BRLRUB',
                                    'HUF' : 'HUFRUB',
                                    'VND' : 'VNDRUB',
                                    'HKD' : 'HKDRUB',
                                    'GEL' : 'GELRUB',
                                    'DKK' : 'DKKRUB',
                                    'AED' : 'AEDRUB',
                                    'USD' : 'USDRUB',
                                    'EUR' : 'EURRUB',
                                    'EGP' : 'EGPRUB',
                                    'INR' : 'INRRUB',
                                    'IDR' : 'IDRRUB',
                                    'KZT' : 'KZTRUB',
                                    'CAD' : 'CADRUB',
                                    'QAR' : 'QARRUB',
                                    'KGS' : 'KGSRUB',
                                    'CNY' : 'CNYRUB',
                                    'MDL' : 'MDLRUB',
                                    'NZD' : 'NZDRUB',
                                    'NOK' : 'NOKRUB',
                                    'PLN' : 'PLNRUB',
                                    'RON' : 'RONRUB',
                                    'XDR' : 'XDRRUB',
                                    'SGD' : 'SGDRUB',
                                    'TJS' : 'TJSRUB',
                                    'THB' : 'THBRUB',
                                    'TRY' : 'TRYRUB',
                                    'TMT' : 'TMTRUB',
                                    'UZS' : 'UZSRUB',
                                    'UAH' : 'UAHRUB',
                                    'CZK' : 'CZKRUB',
                                    'SEK' : 'SEKRUB',
                                    'CHF' : 'CHFRUB',
                                    'RSD' : 'RSDRUB',
                                    'ZAR' : 'ZARRUB',
                                    'KRW' : 'KRWRUB',
                                    'JPY' : 'JPYRUB'}
            # Получаем текущую дату
            current_date = datetime.now().date() #datetime.strptime("2024-01-01", "%Y-%m-%d").date()  #datetime.now().date()

            # Задаем конечную дату (например, "2024-01-01")
            #end_date = datetime.strptime("2023-09-18", "%Y-%m-%d").date()
            end_date = FxPriceData.objects.all().order_by('timestamp').last().timestamp.date()
            # Инициализируем список дат, начиная от текущей и идя к заданной конечной дате
            date_list = []
            while current_date >= end_date:
                date_list.append(current_date)
                current_date -= timedelta(days=1)



            for query_date in date_list:
                formatted_date = query_date.strftime("%d/%m/%Y")
                formatted_date2 = query_date.strftime("%Y-%m-%d")
                full_url = f"{base_url}?date_req={formatted_date}"
                # Выполняем HTTP-запрос
                response = requests.get(full_url)                   
            
            
                # Декодируем содержимое из windows-1251 в строку
                xml_content = response.content.decode("windows-1251")

                # Парсим XML
                root = ET.fromstring(xml_content)

                # Выводим корневой тег
                data = []
                for valute in root.findall("Valute"):
                    code = valute.find("CharCode").text
                    name = valute.find("Name").text
                    value = valute.find("Value").text
                    nominal = valute.find("Nominal").text
                    
                    data.append({"Code": code, "Name": name, "Nominal": nominal, "Value": value})

                df = pd.DataFrame(data)
                quotes_to_create = []
                for item in df.itertuples(index=False):
                    # Ваш код обработки данных
                    sec_id = item.Code
                    if sec_id and sec_id in fx_name:
                        currency = fx_name[sec_id]
                        # Проверка наличия данных
                        
                        existing_quotes = FxPriceData.objects.filter(
                            instrument=sec_id,
                            timestamp=formatted_date2
                        )

                        # Если данные уже существуют, пропускаем текущую итерацию цикла
                        if existing_quotes.exists():
                            continue
                        price = float(item.Value.replace(',', '.'))
                           
                        quote_data = {
                            'timestamp': formatted_date2,
                            'exchange': 'CBR',
                            'instrument': sec_id,
                            'currency': currency,
                            'section': item.Nominal,
                            'price': price
                        }
                        quotes_to_create.append(FxPriceData(**quote_data))
                        #print(f'Data loaded successfully   {instrument}  {contract}  {item.TRADEDATE}')
                        

                if quotes_to_create:
                    FxPriceData.objects.bulk_create(quotes_to_create)
                    print(len(quotes_to_create))
                    #print(df.head())
                    directory = f'data/test/Fxpricedata/'
                    os.makedirs(directory, exist_ok=True)
                    df.to_csv(f"{directory}{formatted_date2}.csv", index=False, encoding="utf-8")
            
            BASEDIR = os.getcwd()
            instruments = FxPriceData.objects.all().values_list('currency', flat=True)
            instruments = list(set(instruments))
            for instrument in instruments:
                fx_quotes = FxPriceData.objects.filter(currency=instrument).order_by('timestamp')
                #timestamp_dates = quotes_contract.values_list('timestamp__date', flat=True)
                

                # Преобразуете значения в формат datetime
                #timestamp_dates = [datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S') for date in timestamp_dates]
                df = pd.DataFrame({
                    'DATETIME': fx_quotes.values_list('timestamp__date', flat=True),
                    'PRICE': fx_quotes.values_list('price', flat=True),
                })#.set_index('<DATE>')
                df['DATETIME'] = pd.to_datetime(df['DATETIME']) + pd.Timedelta('23:00:00')
                #df.index = pd.to_datetime(df['<DATE>'], format='%Y-%m-%d %H:%M:%S').values
                #del df['<DATE>']
                df = df.set_index('DATETIME')
                print(f"{instrument}")
                print(df)
                # Создание каталога, если его нет
                if os.name == 'posix':  # для Unix-подобных систем (например, macOS, Linux)
                    directory = f"{BASEDIR}/data/futures/fx_prices_csv"
                elif os.name == 'nt':   # для Windows
                    directory = f"{BASEDIR}\\data\\futures\\fx_prices_csv"
                os.makedirs(directory, exist_ok=True)
                
                
                # Сохранение в CSV-файл только если есть данные
                if not df.empty:
                    df.to_csv(f'{directory}/{instrument}.csv')
            if os.name == 'posix':  # для Unix-подобных систем (например, macOS, Linux)
                    directory = f"{BASEDIR}/data/futures/fx_prices_csv"
            elif os.name == 'nt':   # для Windows
                    directory = f"{BASEDIR}\\data\\futures\\fx_prices_csv"
            spotfx_from_csv_and_investing_dot_com(directory)
            return json.dumps({'command': 'load_fx_from_cbr', 'status': 'success'}) 

        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise CommandError(f"Error running backtest: {e}")
