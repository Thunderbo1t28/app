import time
from django.core.management.base import BaseCommand
from django.utils import timezone
import pandas as pd
import requests
from datetime import datetime, timedelta
from quotes.models import Quote  






class Command(BaseCommand):
    help = 'Load available instruments into the database'

    def handle(self, *args, **options):
        # Базовый URL
        base_url = "https://iss.moex.com/iss/history/engines/futures/markets/forts/securities.json"

        # Получаем текущую дату
        current_date = datetime.strptime("2019-01-01", "%Y-%m-%d").date()  #datetime.now().date()

        # Задаем конечную дату (например, "2024-01-01")
        end_date = datetime.strptime("2001-01-01", "%Y-%m-%d").date()
        contracts_to_instruments = {'ED': 'ED', 'EG': 'EGBP', 'EJ': 'EJPY', 'Eu': 'Eu', 'EU': 'EURRUBTOM', 'FL': 'FLOT', 'FN': 'FNI', 'FS': 'FEES', 'FV': 'FIVE', 'GD': 'GOLD', 'GK': 'GMKN', 'GL': 'GLDRUBTOM', 'GU': 'GBPU', 'GZ': 'GAZR', 'HK': 'HKD', 'HO': 'HOME', 'HS': 'HANG', 'HY': 'HYDR', 'I2': 'INR', 'IM': 'IMOEX', 'IR': 'IRAO', 'IS': 'ISKJ', 'JP': 'UJPY', 'KM': 'KMAZ', 'KZ': 'KZT', 'LK': 'LKOH', 'MA': 'MMI', 'MC': 'MTLR', 'ME': 'MOEX', 'MF': '1MFR', 'MG': 'MAGN', 'MM': 'MXI', 'MN': 'MGNT', 'MT': 'MTSI', 'MV': 'MVID', 'MX': 'MIX', 'N2': 'NIKK', 'NA': 'NASD', 'NG': 'NG', 'NK': 'NOTK', 'Nl': 'Nl', 'NM': 'NLMK', 'OG': 'OGI', 'OZ': 'OZON', 'PD': 'PLD', 'PH': 'PHOR', 'PI': 'PIKK', 'PO': 'POLY', 'PS': 'POSI', 'PT': 'PLT', 'PZ': 'PLZL', 'RB': 'RGBI', 'RI': 'RTS', 'RL': 'RUAL', 'RM': 'RTSM', 'RN': 'ROSN', 'RR': 'RUON', 'RT': 'RTKM', 'S0': 'SOFL', 'SA': 'SUGR', 'SE': 'SPBE', 'SF': 'SPYF', 'SG': 'SNGP', 'Si': 'Si', 'SN': 'SNGR', 'SO': 'SIBN', 'SP': 'SBPR', 'SR': 'SBRF', 'SS': 'SMLT', 'Su': 'SUGAR', 'SV': 'SILV', 'SX': 'STOX', 'SZ': 'SGZH', 'TI': 'TCSI', 'TN': 'TRNF', 'TR': 'UTRY', 'TT': 'TATN', 'TY': 'TRY', 'UC': 'UCNY', 'US': 'USDRUBTOM', 'VB': 'VTBR', 'VI': 'RVI', 'VK': 'VKCO', 'W4': 'WHEAT', 'WU': 'WUSH', 'YN': 'YNDF', 'Zn': 'Zn', 'AE': 'AED', 'AF': 'AFLT', 'AK': 'AFKS', 'AL': 'ALRS', 'AM': 'ALMN', 'AR': 'AMD', 'AS': 'ASTR', 'AU': 'AUDU', 'BE': 'BELU', 'BN': 'BANE', 'BR': 'BR', 'BS': 'BSPB', 'CA': 'UCAD', 'CF': 'UCHF', 'CH': 'CHMF', 'CM': 'CBOM', 'CN': 'CNYRUBTOM', 'Co': 'Co', 'CR': 'CNY', 'CS': 'CNI', 'DX': 'DAX', 'EC': 'ECAD'}
        contracts_to_secid = {'CNYRUBF' : 'CNYRUBTOM', 'EURRUBF' : 'EURRUBTOM', 'GLDRUBF' : 'GLDRUBTOM', 'IMOEXF' : 'IMOEX', 'USDRUBF' : 'USDRUBTOM'}

        # Инициализируем список дат, начиная от текущей и идя к заданной конечной дате
        date_list = []
        while current_date >= end_date:
            date_list.append(current_date)
            current_date -= timedelta(days=1)



        for query_date in date_list:
            formatted_date = query_date.strftime("%Y-%m-%d")
            full_url = f"{base_url}?date={formatted_date}"

            response_total = requests.get(full_url).json()['history.cursor']['data'][0][1]
            #print(response_total)
            total = int(response_total)
            start = 0
            print(total)
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
                    #print(sec_id)
                    sectype = sec_id[:-7]
                    cleaned_string = ''.join(filter(str.isdigit, sectype))
                    #print(sectype)
                    last_two_chars = sec_id[-7:]
                    #print(sectype)
                    #cleaned_string = ''.join(filter(str.isdigit, last_two_chars[1]))
                    #print(len(sectype))
                    if len(sectype)==2:
                        year_digit = int(sec_id[-4:])
                        month_char = last_two_chars[0]
                        month_mapping = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6, 'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}
                        month = month_mapping.get(month_char, None)
                        #print(last_two_chars)
                        # Проверяем, что контракт присутствует в словаре
                        if sectype and sectype in contracts_to_instruments:
                            instrument = contracts_to_instruments[sectype]
                            #print(f"last_two_chars: {sectype}, instrument: {instrument}")
                            #try:
                                #contract = Quote.objects.filter(sectype=sectype).order_by('timestamp').first()
                            #except Quote.DoesNotExist:
                                #continue
                            #contract_date = item.TRADEDATE[:-10]
                            contract_time = f'{year_digit:04d}{month:02d}00'
                            contract = f'{sectype}_{contract_time}'
                            #print(sectype)
                            #print(contract_time)
                            #print(contract)
                            # Проверка наличия данных
                            existing_quotes = Quote.objects.filter(
                                instrument=instrument,
                                contract=contract,
                                timestamp=item.TRADEDATE
                            )

                            # Если данные уже существуют, пропускаем текущую итерацию цикла
                            if existing_quotes.exists():
                                continue
                            
                            quote_data = {
                                'exchange': 'MOEX',
                                'instrument': instrument,
                                'section': item.BOARDID,
                                'contract': contract,
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
                    
                            
                            #print(f'Data loaded successfully   {instrument}  {sec_id}  {item.TRADEDATE}')

                if quotes_to_create:
                    Quote.objects.bulk_create(quotes_to_create)
                    print(len(quotes_to_create))
                # Увеличиваем значение start для следующего запроса
                start += 100

                #time.sleep(1)