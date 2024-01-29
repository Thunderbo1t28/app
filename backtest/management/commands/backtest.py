from datetime import datetime
from tkinter import S
from django.core.management.base import BaseCommand
import numpy as np
#from quotes.dao import DjangoFuturesSimData
import pandas as pd
from backtest.systems.provided.rules.ewmac import ewmac_forecast_with_defaults as ewmac
from matplotlib.pyplot import show

from quotes.sysdata.sim.csv_futures_sim_data import djangoFuturesSimData


class Command(BaseCommand):
    help = 'Test EWMA Trading Rule using DjangoFuturesSimData'

    def handle(self, *args, **options):
        data = djangoFuturesSimData()
        # Например:
        instrument_code = 'Si'
        currency1='RUB'
        currency2='USD'
        start_date='2024-01-01'
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        #data = sim_data['Si']
        
        price=data.get_instrument_list()
        #price = price.set_index('timestamp')
        #result=ewmac(price, 32, 128)
        #ewmac.tail(5)
        #result.plot()
        #show()
        print(price)
        
        # Выведите результаты в консоль или сделайте что-то еще
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))

