import json
import os
from statistics import correlation
from django.core.management.base import BaseCommand
import yaml
from backtest.models import BacktestResult2
from quotes.models import Quote
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysproduction.reporting.minimum_capital_report import minimum_capital_report
from sysproduction.run_reports import run_reports
from systems.attenuate_vol.vol_attenuation_forecast_scale_cap import volAttenForecastScaleCap
from systems.provided.dynamic_small_system_optimise.accounts_stage import accountForOptimisedStage
from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import optimisedPositions
from systems.provided.rob_system.rawdata import myFuturesRawData
from systems.risk import Risk
from systems.forecasting import Rules
from systems.basesystem import System
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysdata.sim.django_futures_sim_data import djangoFuturesSimData
from sysdata.config.configdata import Config
from systems.forecast_combine import ForecastCombine
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.diagoutput import systemDiag


class Command(BaseCommand):
    help = 'Test EWMA Trading Rule using DjangoFuturesSimData'

    
    def handle(self, *args, **options):
        #callback_function = options['callback']
        #logging.info("Starting backtest_test command...")
        run_reports()
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))
