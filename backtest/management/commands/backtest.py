from datetime import datetime
from tkinter import S
from django.core.management.base import BaseCommand
import numpy as np
#from quotes.dao import DjangoFuturesSimData
import pandas as pd
from backtest.systems.provided.rules.ewmac import ewmac_forecast_with_defaults as ewmac
from matplotlib.pyplot import show
from backtest.systems.trading_rules import TradingRule
from backtest.systems.forecasting import Rules
from backtest.systems.basesystem import System
from quotes.sysdata.sim.django_futures_sim_data import djangoFuturesSimData
from quotes.sysdata.config.configdata import Config
from backtest.systems.forecast_scale_cap import ForecastScaleCap
from backtest.systems.forecast_combine import ForecastCombine


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
        
        price=data.get_backadjusted_futures_price(instrument_code=instrument_code)
        #price = price.set_index('timestamp')
        ewmac_8=TradingRule((ewmac, [], dict(Lfast=8, Lslow=32))) ## as a tuple (function, data, other_args) notice the empty element in the middle
        ewmac_32=TradingRule(dict(function=ewmac, other_args=dict(Lfast=32, Lslow=128)))  ## as a dict
        #my_rules=Rules(dict(ewmac8=ewmac_8, ewmac32=ewmac_32))
        #my_system=System([my_rules], data)
        my_config=Config()
        empty_rules=Rules()
        my_config.trading_rules=dict(ewmac8=ewmac_8, ewmac32=ewmac_32)
        my_config.instruments=["Si", "SPYF", "GOLD", "MXI"]
        my_config.use_forecast_scale_estimates=True
        fcs=ForecastScaleCap()
        #my_system = System([fcs, empty_rules], data, my_config)
        #my_system=System([empty_rules], data, my_config)
        combiner = ForecastCombine()
        my_system = System([fcs, empty_rules, combiner], data, my_config)
        print(my_system.combForecast.get_forecast_weights("Si").tail(5))
        print(my_system.combForecast.get_forecast_diversification_multiplier("Si").tail(5))
        #print(my_system.forecastScaleCap.get_forecast_scalar("Si", "ewmac32").tail(5))
        #ewmac.tail(5)
        #result.plot()
        #show()
        #print(my_config)
        
        # Выведите результаты в консоль или сделайте что-то еще
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))

