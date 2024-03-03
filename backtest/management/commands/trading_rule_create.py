import json
from django.core.management.base import BaseCommand
from backtest.models import BacktestResult, MyConfigModel, TradingRuleModel
from systems.provided.rules.ewmac import ewmac_forecast_with_defaults as ewmac
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
import logging


class Command(BaseCommand):
    help = 'Test EWMA Trading Rule using DjangoFuturesSimData'

    
    def handle(self, *args, **options):
        #callback_function = options['callback']
        #logging.info("Starting backtest_test command...")
        TradingRuleModel.objects.create(
            name='breakout10',
            function='systems.provided.rules.breakout.breakout',
            data=['rawdata.get_daily_prices'],
            other_args={'lookback': 10}
        )
        TradingRuleModel.objects.create(
            name='breakout20',
            function='systems.provided.rules.breakout.breakout',
            data=['rawdata.get_daily_prices'],
            other_args={'lookback': 20}
        )
        TradingRuleModel.objects.create(
            name='breakout40',
            function='systems.provided.rules.breakout.breakout',
            data=['rawdata.get_daily_prices'],
            other_args={'lookback': 40}
        )
        TradingRuleModel.objects.create(
            name='breakout80',
            function='systems.provided.rules.breakout.breakout',
            data=['rawdata.get_daily_prices'],
            other_args={'lookback': 80}
        )
        TradingRuleModel.objects.create(
            name='breakout160',
            function='systems.provided.rules.breakout.breakout',
            data=['rawdata.get_daily_prices'],
            other_args={'lookback': 160}
        )
        TradingRuleModel.objects.create(
            name='breakout320',
            function='systems.provided.rules.breakout.breakout',
            data=['rawdata.get_daily_prices'],
            other_args={'lookback': 320}
        )
        TradingRuleModel.objects.create(
            name='relmomentum10',
            function='systems.provided.rules.rel_mom.relative_momentum',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns','rawdata.normalised_price_for_asset_class'],
            other_args={'horizon': 10}
        )
        TradingRuleModel.objects.create(
            name='relmomentum20',
            function='systems.provided.rules.rel_mom.relative_momentum',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns','rawdata.normalised_price_for_asset_class'],
            other_args={'horizon': 20}
        )
        TradingRuleModel.objects.create(
            name='relmomentum40',
            function='systems.provided.rules.rel_mom.relative_momentum',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns','rawdata.normalised_price_for_asset_class'],
            other_args={'horizon': 40}
        )
        TradingRuleModel.objects.create(
            name='relmomentum80',
            function='systems.provided.rules.rel_mom.relative_momentum',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns','rawdata.normalised_price_for_asset_class'],
            other_args={'horizon': 80}
        )
        TradingRuleModel.objects.create(
            name='mrinasset1000',
            function='systems.provided.rules.cs_mr.cross_sectional_mean_reversion',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns','rawdata.normalised_price_for_asset_class'],
            other_args={'horizon': 1000}
        )
        TradingRuleModel.objects.create(
            name='carry10',
            function='systems.provided.rules.carry.carry',
            data=['rawdata.raw_carry'],
            other_args={'smooth_days': 10}
        )
        TradingRuleModel.objects.create(
            name='carry30',
            function='systems.provided.rules.carry.carry',
            data=['rawdata.raw_carry'],
            other_args={'smooth_days': 30}
        )
        TradingRuleModel.objects.create(
            name='carry60',
            function='systems.provided.rules.carry.carry',
            data=['rawdata.raw_carry'],
            other_args={'smooth_days': 60}
        )
        TradingRuleModel.objects.create(
            name='carry125',
            function='systems.provided.rules.carry.carry',
            data=['rawdata.raw_carry'],
            other_args={'smooth_days': 125}
        )
        TradingRuleModel.objects.create(
            name='assettrend2',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.normalised_price_for_asset_class'],
            other_args={'Lfast': 2, 'Lslow': 8}
        )
        TradingRuleModel.objects.create(
            name='assettrend4',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.normalised_price_for_asset_class'],
            other_args={'Lfast': 4, 'Lslow': 16}
        )
        TradingRuleModel.objects.create(
            name='assettrend8',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.normalised_price_for_asset_class'],
            other_args={'Lfast': 8, 'Lslow': 32}
        )
        TradingRuleModel.objects.create(
            name='assettrend16',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.normalised_price_for_asset_class'],
            other_args={'Lfast': 16, 'Lslow': 64}
        )
        TradingRuleModel.objects.create(
            name='assettrend32',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.normalised_price_for_asset_class'],
            other_args={'Lfast': 32, 'Lslow': 128}
        )
        TradingRuleModel.objects.create(
            name='assettrend64',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.normalised_price_for_asset_class'],
            other_args={'Lfast': 64, 'Lslow': 256}
        )
        TradingRuleModel.objects.create(
            name='normmom2',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns'],
            other_args={'Lfast': 2, 'Lslow': 8}
        )
        TradingRuleModel.objects.create(
            name='normmom4',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns'],
            other_args={'Lfast': 4, 'Lslow': 16}
        )
        TradingRuleModel.objects.create(
            name='normmom8',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns'],
            other_args={'Lfast': 8, 'Lslow': 32}
        )
        TradingRuleModel.objects.create(
            name='normmom16',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns'],
            other_args={'Lfast': 16, 'Lslow': 64}
        )
        TradingRuleModel.objects.create(
            name='normmom32',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns'],
            other_args={'Lfast': 32, 'Lslow': 128}
        )
        TradingRuleModel.objects.create(
            name='normmom64',
            function='systems.provided.rules.ewmac.ewmac_calc_vol',
            data=['rawdata.get_cumulative_daily_vol_normalised_returns'],
            other_args={'Lfast': 64, 'Lslow': 256}
        )
        TradingRuleModel.objects.create(
            name='momentum4',
            function='systems.provided.rules.ewmac.ewmac',
            data=['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'],
            other_args={'Lfast': 4, 'Lslow': 16}
        )
        TradingRuleModel.objects.create(
            name='momentum8',
            function='systems.provided.rules.ewmac.ewmac',
            data=['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'],
            other_args={'Lfast': 8, 'Lslow': 32}
        )
        TradingRuleModel.objects.create(
            name='momentum16',
            function='systems.provided.rules.ewmac.ewmac',
            data=['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'],
            other_args={'Lfast': 16, 'Lslow': 64}
        )
        TradingRuleModel.objects.create(
            name='momentum32',
            function='systems.provided.rules.ewmac.ewmac',
            data=['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'],
            other_args={'Lfast': 32, 'Lslow': 128}
        )
        TradingRuleModel.objects.create(
            name='momentum64',
            function='systems.provided.rules.ewmac.ewmac',
            data=['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'],
            other_args={'Lfast': 64, 'Lslow': 256}
        )
        TradingRuleModel.objects.create(
            name='relcarry',
            function='systems.provided.rules.carry.relative_carry',
            data=['rawdata.smoothed_carry', 'rawdata.median_carry_for_asset_class'],
            other_args=''
        )
        TradingRuleModel.objects.create(
            name='skewabs365',
            function='systems.provided.rules.factors.factor_trading_rule',
            data=['rawdata.get_demeanded_factor_value'],
            other_args={'smooth': 90, '_factor_name': 'neg_skew', 
                        '_demean_method': 'historic_average_factor_value_all_assets',
                        '_lookback_days': 365}
        )
        TradingRuleModel.objects.create(
            name='skewabs180',
            function='systems.provided.rules.factors.factor_trading_rule',
            data=['rawdata.get_demeanded_factor_value'],
            other_args={'smooth': 45, '_factor_name': 'neg_skew', 
                        '_demean_method': 'historic_average_factor_value_all_assets',
                        '_lookback_days': 180}
        )
        TradingRuleModel.objects.create(
            name='skewrv365',
            function='systems.provided.rules.factors.factor_trading_rule',
            data=['rawdata.get_demeanded_factor_value'],
            other_args={'smooth': 90, '_factor_name': 'neg_skew', 
                        '_demean_method': 'average_factor_value_in_asset_class_for_instrument',
                        '_lookback_days': 365}
        )
        TradingRuleModel.objects.create(
            name='skewrv180',
            function='systems.provided.rules.factors.factor_trading_rule',
            data=['rawdata.get_demeanded_factor_value'],
            other_args={'smooth': 45, '_factor_name': 'neg_skew', 
                        '_demean_method': 'average_factor_value_in_asset_class_for_instrument',
                        '_lookback_days': 180}
        )
        TradingRuleModel.objects.create(
            name='accel16',
            function='systems.provided.rules.accel.accel',
            data=['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'],
            other_args={'Lfast': 16}
        )
        TradingRuleModel.objects.create(
            name='accel32',
            function='systems.provided.rules.accel.accel',
            data=['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'],
            other_args={'Lfast': 32}
        )
        TradingRuleModel.objects.create(
            name='accel64',
            function='systems.provided.rules.accel.accel',
            data=['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'],
            other_args={'Lfast': 64}
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))
