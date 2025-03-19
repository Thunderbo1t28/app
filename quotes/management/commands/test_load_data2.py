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




# Настройка логирования
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load data to database'

      

    def handle(self, *args, **options):
        # Отладочное логирование для проверки аргументов
        try:
                               
            BASEDIR = os.getcwd()
            csv_multiple_data_path = f"{BASEDIR}\\data\\futures\\multiple_prices_csv"
            csv_roll_data_path = f"{BASEDIR}\\data\\futures\\roll_calendars_csv"
            
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
