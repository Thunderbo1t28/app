from locale import currency
import os
from django.db.models import Max, F
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.db import transaction
import pandas as pd
from quotes.models import FxPriceData, Instrument, LastDownloadDate, Quote, RollCalendar
from quotes.utils.contracts_utils import find_current_next_contracts_for_instruments

class Command(BaseCommand):
    help = 'Find current and next contracts for instruments and save to RollCalendar model'

    def handle(self, *args, **options):
        '''
        # Получаем последние даты торгов для каждого контракта
        last_trading_dates = LastDownloadDate.objects.annotate(
            max_trading_date=Max('last_download_date')
        ).values('id', 'contract', 'max_trading_date')

        # Обновляем is_active для контрактов, у которых последняя дата торгов совпадает с именем контракта
        for contract_data in last_trading_dates:
            contract_name = contract_data['contract']
            max_trading_date = contract_data['max_trading_date']
            
            # Преобразование имени контракта в формат даты для сравнения
            contract_date = datetime.strptime(contract_name, '%Y%m%d').date()
            
            if max_trading_date.date() == contract_date:
                LastDownloadDate.objects.filter(id=contract_data['id']).update(is_active=False)
        '''
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

                