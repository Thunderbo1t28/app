from datetime import datetime
import json
from tkinter import S
from django.core.management.base import BaseCommand
import numpy as np
#from quotes.dao import DjangoFuturesSimData
import pandas as pd
from backtest.models import BacktestResult
from systems.provided.rules.ewmac import ewmac_forecast_with_defaults as ewmac
from matplotlib.pyplot import show
from systems.trading_rules import TradingRule
from systems.forecasting import Rules
from systems.basesystem import System
from sysdata.sim.django_futures_sim_data import djangoFuturesSimData
from sysdata.config.configdata import Config
from systems.forecast_scale_cap import ForecastScaleCap
from systems.forecast_combine import ForecastCombine
from systems.rawdata import RawData
from systems.positionsizing import PositionSizing
from systems.accounts.accounts_stage import Account
from systems.portfolio import Portfolios

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
        my_rules=Rules(dict(ewmac8=ewmac_8, ewmac32=ewmac_32))
        #my_system=System([my_rules], data)
        my_config=Config()
        empty_rules=Rules()
        my_config.trading_rules=dict(ewmac8=ewmac_8, ewmac32=ewmac_32)
        my_config.instruments=["Si", "BR", "GOLD", "NG", "Eu", "MXI"]
        my_config.use_forecast_scale_estimates=True
        fcs=ForecastScaleCap()
        #my_system = System([fcs, empty_rules], data, my_config)
        #my_system=System([empty_rules], data, my_config)
        combiner = ForecastCombine()
        raw_data = RawData()
        position_size = PositionSizing()
        my_account = Account()

        my_config.forecast_weight_estimate = dict(method="one_period")
        
        my_config.percentage_vol_target=25
        my_config.notional_trading_capital=5000000
        my_config.base_currency="RUB"
        portfolio = Portfolios()

        ## Using shrinkage will speed things but - but I don't recommend it for actual trading...
        my_config.use_instrument_weight_estimates = True
        my_config.use_instrument_div_mult_estimates = True
        my_config.instrument_weight_estimate=dict(method="shrinkage", date_method="in_sample") ## speeds things up

        my_system = System([my_account, fcs, my_rules, combiner, position_size, raw_data,
                            portfolio], data, my_config)

        profits=my_system.accounts.portfolio()
        # Преобразование результатов в формат JSON
        metrics_json = json.dumps(profits.percent.stats())
        additional_info_json = json.dumps(profits.gross.percent.stats())

        # Сохранение результатов в базе данных
        backtest_result = BacktestResult(metrics=metrics_json, additional_info=additional_info_json)
        backtest_result.save()
        #print(my_system.forecastScaleCap.get_forecast_scalar("Si", "ewmac32").tail(5))
        #ewmac.tail(5)
        #result.plot()
        #show()
        #print(my_config)
        
        # Выведите результаты в консоль или сделайте что-то еще
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))

