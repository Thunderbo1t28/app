import json
from django.core.management.base import BaseCommand
from backtest.models import BacktestResult, MyConfigModel, TradingRuleModel
from backtest.systems.provided.rules.ewmac import ewmac_forecast_with_defaults as ewmac
from backtest.systems.trading_rules import TradingRule
from backtest.systems.forecasting import Rules
from backtest.systems.basesystem import System
from quotes.sysdata.sim.django_futures_sim_data import djangoFuturesSimData
from quotes.sysdata.config.configdata import Config
from backtest.systems.forecast_scale_cap import ForecastScaleCap
from backtest.systems.forecast_combine import ForecastCombine
from backtest.systems.rawdata import RawData
from backtest.systems.positionsizing import PositionSizing
from backtest.systems.accounts.accounts_stage import Account
from backtest.systems.portfolio import Portfolios
import logging


class Command(BaseCommand):
    help = 'Test EWMA Trading Rule using DjangoFuturesSimData'

    def add_arguments(self, parser):
        parser.add_argument('trading_rules', nargs='+', type=str)

        #parser.add_argument('--callback', dest='callback', type=str, default=None, help='Specify the callback function')

    def handle(self, *args, **options):
        #callback_function = options['callback']
        #logging.info("Starting backtest_test command...")
        data = djangoFuturesSimData()
        empty_rules = Rules()
        my_config = Config()
        # Получение аргументов из командной строки по их именам
        trading_rules_list = options['trading_rules']
        my_config.trading_rules = {}
        for item in trading_rules_list:
            trading_rule = TradingRuleModel.objects.get(name=item)
            my_config.trading_rules[item] = TradingRule(
                dict(function=trading_rule.function,
                data=trading_rule.data,
                other_args=trading_rule.other_args
            ))
        #config = MyConfigModel.objects.get(id=config_id)
        # Создание объекта Config с полученными параметрами
        
        

        fcs = ForecastScaleCap()
        portfolio = Portfolios()
        combiner = ForecastCombine()
        raw_data = RawData()
        position_size = PositionSizing()
        my_account = Account()

        my_config.instruments = ["Si", "BR", "GOLD", "NG", "Eu", "MXI", "MOEX", "ALRS",
                                 "SILV", "SBRF", "GAZR", "ROSN", "MAGN", "SPYF", "NASD"]
        my_config.use_forecast_scale_estimates = True
        my_config.forecast_weight_estimate = dict(method="one_period")
        my_config.percentage_vol_target = 25
        my_config.notional_trading_capital = 5000000
        my_config.base_currency = "RUB"
        my_config.use_instrument_weight_estimates = True
        my_config.use_instrument_div_mult_estimates = True
        my_config.instrument_weight_estimate = dict(method="shrinkage", date_method="in_sample")

        my_system = System([my_account, fcs, empty_rules, combiner, position_size, raw_data, portfolio], data, my_config)

        profits = my_system.accounts.portfolio()

        # Преобразование результатов в формат JSON
        metrics_json = json.dumps(profits.percent.stats())
        additional_info_json = json.dumps(profits.gross.percent.stats())

        # Сохранение результатов в базе данных
        backtest_result = BacktestResult(metrics=metrics_json, additional_info=additional_info_json)
        backtest_result.save()
        # Вызов колбэка и передача ему результатов
        #if 'callback' in options and callable(options['callback']):
            #options['callback'](metrics_json, additional_info_json)
        # Вывод успешного завершения теста
        #logging.info("Command executed successfully.")
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))
