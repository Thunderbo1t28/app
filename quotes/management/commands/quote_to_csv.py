import os
from django.db.models import Max, F
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.db import transaction
import pandas as pd
from quotes.models import Instrument, LastDownloadDate, Quote, RollCalendar
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
        instruments = Instrument.objects.all()
        for instrument in instruments:
            # Получаем активные контракты для данного инструмента
            active_contracts = LastDownloadDate.objects.filter(instrument=instrument, is_active=True).values_list('contract', flat=True)
            #active_contracts = Quote.objects.filter(instrument=instrument).values_list('contract', flat=True)
            quotes = Quote.objects.filter(instrument=instrument).order_by('timestamp')
            contract_list = quotes.values_list('contract', flat=True).distinct()
            contract_list = list(set(contract_list))
            for contract in contract_list:
                quotes_contract = quotes.filter(contract=contract)

                df = pd.DataFrame({
                    '<DATE>': quotes_contract.values_list('timestamp__date', flat=True),
                    '<TIME>': '00:00:00',
                    '<OPEN>': quotes_contract.values_list('open_price', flat=True),
                    '<HIGH>': quotes_contract.values_list('high_price', flat=True),
                    '<LOW>': quotes_contract.values_list('low_price', flat=True),
                    '<CLOSE>': quotes_contract.values_list('close_price', flat=True),
                    '<VOL>': quotes_contract.values_list('volume', flat=True),
                }).set_index('<DATE>')
                print(f"{instrument}")
                print(df)
                # Создание каталога, если его нет
                directory = f'downloadData/'
                os.makedirs(directory, exist_ok=True)

                # Сохранение в CSV-файл только если есть данные
                if not df.empty:
                    df.to_csv(f'{directory}/{instrument}_{contract}.csv')

                    # Обновление или создание записи о последней загрузке
                    last_date = df.index.max()
                    LastDownloadDate.objects.update_or_create(
                        instrument=instrument,
                        contract=contract,
                        defaults={'last_download_date': last_date}
                    )