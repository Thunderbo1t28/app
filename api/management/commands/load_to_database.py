from django.core.management.base import BaseCommand, CommandError
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysinit.futures.adjustedprices_from_mongo_multiple_to_mongo import process_adjusted_prices_all_instruments
from sysinit.futures.contract_prices_from_csv_to_arctic import init_arctic_with_csv_futures_contract_prices
from sysinit.futures.multipleprices_from_arcticprices_and_csv_calendars_to_arctic import process_multiple_prices_all_instruments
import json
import os
import logging
import time
from django.core.management.base import BaseCommand
#from django.utils import timezone
import pandas as pd
import requests
from datetime import datetime, timedelta
from quotes.models import Instrument, LastDownloadDate, Quote
from django.db.models import Max




# Настройка логирования
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load data to database'

      

    def handle(self, *args, **options):
        # Отладочное логирование для проверки аргументов
        try:
            # Базовый URL
            base_url = "https://iss.moex.com/iss/history/engines/futures/markets/forts/securities.json"
            # Получаем текущую дату
            current_date = datetime.now().date() #datetime.strptime("2020-01-01", "%Y-%m-%d").date()  #datetime.now().date()
            # Задаем конечную дату (например, "2024-01-01")
            #end_date = datetime.strptime("2010-01-01", "%Y-%m-%d").date()
            end_date = Quote.objects.all().order_by('timestamp').last().timestamp.date()
            contracts_to_instruments = {'ED': 'ED',   'Eu': 'Eu', 
                                        'FL': 'FLOT', 'FN': 'FNI',  
                                        'GD': 'GOLD', 'GK': 'GMKN',  'GU': 'GBPU', 'GZ': 'GAZR',
                                            'HK': 'HKD', 'HO': 'HOME', 'HS': 'HANG', 'HY': 'HYDR', 'I2': 'INR',
                                                'IS': 'ISKJ',  'KM': 'KMAZ', 
                                            'KZ': 'KZT', 'LK': 'LKOH',  'MC': 'MTLR', 'ME': 'MOEX', 
                                            'MG': 'MAGN', 'MM': 'MXI', 'MN': 'MGNT', 'MT': 'MTSI', 
                                            'MV': 'MVID', 'MX': 'MIX',  'NA': 'NASD', 'NG': 'NG', 
                                            'NK': 'NOTK',  'NM': 'NLMK', 'OG': 'OGI',  
                                            'PD': 'PLD', 'PH': 'PHOR', 'PI': 'PIKK', 'PO': 'POLY', 'PS': 'POSI', 
                                            'PT': 'PLT', 'PZ': 'PLZL', 'RB': 'RGBI', 'RI': 'RTS', 'RL': 'RUAL', 
                                            'RM': 'RTSM', 'RN': 'ROSN',  'RT': 'RTKM',  
                                            'SE': 'SPBE', 'SF': 'SPYF', 'SG': 'SNGP', 'Si': 'Si', 
                                            'SN': 'SNGR', 'SO': 'SIBN', 'SP': 'SBPR', 'SR': 'SBRF', 'SS': 'SMLT', 
                                            'Su': 'SUGAR', 'SV': 'SILV', 'SX': 'STOX', 'SZ': 'SGZH', #'JP': 'UJPY', 'OZ': 'OZON', 'YN': 'YNDF', 'FV': 'FIVE',
                                                'TT': 'TATN', 'TY': 'TRY', 'UC': 'UCNY', #'MA': 'MMI','RR': 'RUON','N2': 'NIKK','CF': 'UCHF',
                                                'VK': 'VKCO', 'W4': 'WHEAT', #'EG': 'EGBP','IR': 'IRAO','EJ': 'EJPY','Co': 'Co','MF': '1MFR','TR': 'UTRY',
                                            'WU': 'WUSH',  'AE': 'AED', 'AF': 'AFLT', #'SA': 'SUGR','TI': 'TCSI', 'TN': 'TRNF',
                                            'AK': 'AFKS', 'AL': 'ALRS',    #'AM': 'ALMN','AR': 'AMD','AS': 'ASTR','Nl': 'Nl','VI': 'RVI','S0': 'SOFL',
                                            'AU': 'AUDU', 'BE': 'BELU', 'BN': 'BANE', 'BR': 'BR', 'BS': 'BSPB', #'CA': 'UCAD',
                                                'CH': 'CHMF', 'CM': 'CBOM', #'CN': 'CNYRUBTOM', 'EC': 'ECAD','Zn': 'Zn',
                                            'CR': 'CNY', 'CS': 'CNI', 'DX': 'DAX', 'VB': 'VTBR','FS': 'FEES',} 

            # Инициализируем список дат, начиная от текущей и идя к заданной конечной дате
            date_list = []
            while current_date >= end_date:
                date_list.append(current_date)
                current_date -= timedelta(days=1)

            date_list = sorted(set(date_list), reverse=False)
            for query_date in date_list:
                formatted_date = query_date.strftime("%Y-%m-%d")
                full_url = f"{base_url}?date={formatted_date}"
                response_total = requests.get(full_url).json()['history.cursor']['data'][0][1]
                total = int(response_total)
                start = 0
                while start < total:
                    # Добавляем параметры start и total к URL
                    page_url = f"{full_url}&start={start}&total={min(100, total - start)}"
                    #print('1')
                    # Выполняем HTTP-запрос
                    response = requests.get(page_url)
                    response_data = response.json()['history']['data']
                    response_columns = response.json()['history']['columns']
                    response_df = pd.DataFrame(response_data, columns=response_columns)
                    # Обрабатываем данные и добавляем в базу данных
                    quotes_to_create = []
                    #print("1")
                    for item in response_df.itertuples(index=False):
                        # Ваш код обработки данных
                        sec_id = item.SECID
                        sectype = sec_id[:-7]
                        
                        sectype2 = sec_id[:-2]
                        if len(sectype)==2:
                            
                            # Проверяем, что контракт присутствует в словаре
                            if sectype and sectype in contracts_to_instruments:
                                instrument = contracts_to_instruments[sectype]
                                if pd.notna(item.TRADEDATE) and pd.notna(item.OPEN) and pd.notna(item.LOW) and pd.notna(item.HIGH) and pd.notna(item.CLOSE) and pd.notna(item.VOLUME):
                                    existing_quotes = Quote.objects.filter(
                                        instrument=instrument,
                                        secid=sec_id,
                                        timestamp=item.TRADEDATE
                                    )
                                    # Если данные уже существуют, пропускаем текущую итерацию цикла
                                    if existing_quotes.exists():
                                        continue
                                    '''contract_try = Quote.objects.filter(
                                        instrument=instrument,
                                        secid=sec_id
                                    )'''
                                    contract_month = sec_id[2:-6]
                                    contract_year = sec_id[5:]
                                    #print(contract_year)
                                    month_letters = "FGHJKMNQUVXZ"
                                    month_number = month_letters.index(contract_month) + 1  # Индексация начинается с 0, поэтому добавляем 1
                                    month_str = str(month_number).zfill(2)
                                    contract_concat = f"{contract_year}{month_str}00"
                                    #contract_date = datetime.strptime(item.TRADEDATE, "%Y-%m-%d").strftime("%Y%m%d")
                                    #contract_try.update(contract=contract_date)
                                    quote_data = {
                                        'exchange': 'MOEX',
                                        'instrument': instrument,
                                        'section': item.BOARDID,
                                        'contract': contract_concat,
                                        'sectype': sectype,
                                        'secid': sec_id,
                                        'open_price': item.OPEN,
                                        'low_price': item.LOW,
                                        'high_price': item.HIGH,
                                        'close_price': item.CLOSE,
                                        'volume': item.VOLUME,
                                        'timestamp': item.TRADEDATE
                                    }
                                    quotes_to_create.append(Quote(**quote_data))
                                    #print(f'Data loaded successfully   {instrument}  {contract}  {item.TRADEDATE}')
                                    
                        elif len(sectype2)==2:
                            if sectype2 and sectype2 in contracts_to_instruments:
                                instrument = contracts_to_instruments[sectype2]
                                
                                if pd.notna(item.TRADEDATE) and pd.notna(item.OPEN) and pd.notna(item.LOW) and pd.notna(item.HIGH) and pd.notna(item.CLOSE) and pd.notna(item.VOLUME):
                                    existing_quotes = Quote.objects.filter(
                                        instrument=instrument,
                                        secid=sec_id,
                                        timestamp=item.TRADEDATE
                                    )
                                    # Если данные уже существуют, пропускаем текущую итерацию цикла
                                    if existing_quotes.exists():
                                        continue
                                    '''contract_try = Quote.objects.filter(
                                        instrument=instrument,
                                        secid=sec_id
                                    )'''
                                    contract_month = sec_id[-2:-1]
                                    contract_year = sec_id[3:]
                                    month_letters = "FGHJKMNQUVXZ"
                                    month_number = month_letters.index(contract_month) + 1  # Индексация начинается с 0, поэтому добавляем 1
                                    month_str = str(month_number).zfill(2)
                                    
                                    # Словарь для соответствия цифровых значений года и соответствующего года в формате строки
                                    year_mapping = {
                                        '9': '2019',
                                        '0': '2020',
                                        '1': '2021',
                                        '2': '2022',
                                        '3': '2023',
                                        '4': '2024',
                                        '5': '2025',
                                        '6': '2026',
                                        '7': '2027',
                                        '8': '2018',
                                        # Добавьте дополнительные соответствия по мере необходимости
                                    }
                                    # Преобразование года в формат строки
                                    #print(month_str)
                                    contract_year_str = year_mapping.get(contract_year, 'Unknown')
                                    #print(contract_year_str)
                                    contract_concat = f"{contract_year_str}{month_str}00"
                                    #contract_date = datetime.strptime(item.TRADEDATE, "%Y-%m-%d").strftime("%Y%m%d")
                                    #contract_try.update(contract=contract_date)
                                    quote_data = {
                                        'exchange': 'MOEX',
                                        'instrument': instrument,
                                        'section': item.BOARDID,
                                        'contract': contract_concat,
                                        'sectype': sectype2,
                                        'secid': sec_id,
                                        'open_price': item.OPEN,
                                        'low_price': item.LOW,
                                        'high_price': item.HIGH,
                                        'close_price': item.CLOSE,
                                        'volume': item.VOLUME,
                                        'timestamp': item.TRADEDATE
                                    }
                                    quotes_to_create.append(Quote(**quote_data))
                            #print(f'Data loaded successfully   {instrument}  {sec_id}  {item.TRADEDATE}')
                    if quotes_to_create:
                        Quote.objects.bulk_create(quotes_to_create)
                        print(len(quotes_to_create))
                    # Увеличиваем значение start для следующего запроса
                    start += 100

                    time.sleep(1)
            last_trading_dates = LastDownloadDate.objects.annotate(
                max_trading_date=Max('last_download_date')
            ).values('id', 'contract', 'max_trading_date')
            contract_date = datetime.now().date()
            contract_date -= timedelta(days=180)
            # Обновляем is_active для контрактов, у которых последняя дата торгов совпадает с именем контракта
            for contract_data in last_trading_dates:
                contract_name = contract_data['contract']
                max_trading_date = contract_data['max_trading_date']
                
                # Преобразование имени контракта в формат даты для сравнения
                #contract_date = datetime.strptime(contract_name, '%Y%m%d').date()
                #contract_date = datetime.now().date()
                #contract_date -= timedelta(days=1)
                if max_trading_date.date() < contract_date:
                    LastDownloadDate.objects.filter(id=contract_data['id']).update(is_active=False)
            
            instruments = Instrument.objects.all()
            for instrument in instruments:
                # Получаем активные контракты для данного инструмента
                active_contracts = LastDownloadDate.objects.filter(instrument=instrument, is_active=True).values_list('contract', flat=True)
                #active_contracts = Quote.objects.filter(instrument=instrument).values_list('contract', flat=True)
                quotes = Quote.objects.filter(instrument=instrument).order_by('timestamp')
                contract_list = quotes.values_list('contract', flat=True).distinct()
                contract_list = list(set(contract_list))
                active_contracts = list(set(active_contracts))
                for contract in active_contracts:
                    quotes_contract = quotes.filter(contract=contract)
                    #timestamp_dates = quotes_contract.values_list('timestamp__date', flat=True)
                    

                    # Преобразуете значения в формат datetime
                    #timestamp_dates = [datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S') for date in timestamp_dates]
                    df = pd.DataFrame({
                        '<DATE>': quotes_contract.values_list('timestamp__date', flat=True),
                        '<OPEN>': quotes_contract.values_list('open_price', flat=True),
                        '<HIGH>': quotes_contract.values_list('high_price', flat=True),
                        '<LOW>': quotes_contract.values_list('low_price', flat=True),
                        '<CLOSE>': quotes_contract.values_list('close_price', flat=True),
                        '<VOL>': quotes_contract.values_list('volume', flat=True),
                    })#.set_index('<DATE>')
                    df['<DATE>'] = pd.to_datetime(df['<DATE>']) + pd.Timedelta('23:00:00')
                    #df.index = pd.to_datetime(df['<DATE>'], format='%Y-%m-%d %H:%M:%S').values
                    #del df['<DATE>']
                    df = df.set_index('<DATE>')
                    print(f"{instrument}")
                    print(df)
                    # Создание каталога, если его нет
                    directory = f'downloadData/'
                    os.makedirs(directory, exist_ok=True)
                    contract_name = contract[:-2]

                    # Сохранение в CSV-файл только если есть данные
                    if not df.empty:
                        df.to_csv(f'{directory}/{instrument}_{contract_name}00.csv')

                        # Обновление или создание записи о последней загрузке
                        last_date = df.index.max()
                        LastDownloadDate.objects.update_or_create(
                            instrument=instrument,
                            contract=contract,
                            defaults={'last_download_date': last_date})
                          
            barchart_csv_config = ConfigCsvFuturesPrices(
                input_date_index_name="<DATE>",
                input_skiprows=0,
                input_skipfooter=0,
                input_date_format="%Y-%m-%d %H:%M:%S",
                input_column_mapping=dict(
                    OPEN="<OPEN>", HIGH="<HIGH>", LOW="<LOW>", FINAL="<CLOSE>", VOLUME="<VOL>"
                ),
            )
            BASEDIR = os.getcwd()
            datapath = BASEDIR + "/downloadData"
            csv_multiple_data_path = f"{BASEDIR}\\data\\futures\\multiple_prices_csv"
            csv_roll_data_path = f"{BASEDIR}\\data\\futures\\roll_calendars_csv"
            
            init_arctic_with_csv_futures_contract_prices(datapath, csv_config=barchart_csv_config)
            process_multiple_prices_all_instruments(
                csv_multiple_data_path=csv_multiple_data_path,
                csv_roll_data_path=csv_roll_data_path,
            )

            process_adjusted_prices_all_instruments(
                ADD_TO_ARCTIC=True, ADD_TO_CSV=True, csv_adj_data_path=f"{BASEDIR}\\data\\futures\\adjusted_prices_csv"
            )

            return json.dumps({'command': 'load_to_database', 'status': 'success'}) 

        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise CommandError(f"Error running backtest: {e}")
