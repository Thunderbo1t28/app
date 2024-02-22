import os
import re
from django.db.models import Max, F
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.db import transaction
import pandas as pd
from quotes.models import Instrument, LastDownloadDate, Quote, RollCalendar, SpreadCosts
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
        spreads = [{}]
        instruments = Instrument.objects.all()
        for instrument in instruments:
            quotes = SpreadCosts.objects.filter(instrument=instrument)
            if quotes.exists():
                spreadcost_value = quotes[0].spreadcost
            else:
                spreadcost_value = None
            dict_spread = {'Instrument': str(instrument), 'SpreadCost': spreadcost_value}
            spreads.append(dict_spread)
        #print(spreads)    
        df = pd.DataFrame(spreads)
        # Создание каталога, если его нет
        directory = f"{BASEDIR}\\data\\futures\\csvconfig"
        os.makedirs(directory, exist_ok=True)
        
        # Сохранение в CSV-файл только если есть данные
        if not df.empty:
            df.to_csv(f'{directory}/spreadcosts.csv', index=False)
                