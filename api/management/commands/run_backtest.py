from django.core.management.base import BaseCommand, CommandError
from celery.result import AsyncResult
from numpy import save
from systems.basesystem import System
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysdata.config.configdata import Config
from systems.forecast_combine import ForecastCombine
from systems.provided.attenuate_vol.vol_attenuation_forecast_scale_cap import volAttenForecastScaleCap
from systems.provided.rob_system.rawdata import myFuturesRawData
from systems.risk import Risk
from systems.provided.dynamic_small_system_optimise.accounts_stage import accountForOptimisedStage
from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import optimisedPositions
from systems.forecasting import Rules
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.diagoutput import systemDiag
from backtest.models import BacktestResult2
import json
import os
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run Backtest'

    def add_arguments(self, parser):

        parser.add_argument(
            'instrument',
            type=str,
            nargs='+',
            help='List of instruments'
        )
        parser.add_argument('currency', type=str)
        parser.add_argument('capital', type=float)
        parser.add_argument('target', type=float)

    def handle(self, *args, **options):
        # Отладочное логирование для проверки аргументов
        logger.info(f"Args: {args}")
        logger.info(f"Options: {options}")
        instrument = options.get('instrument', ['AFKS, ALRS'])
        currency = options.get('currency')
        capital = options.get('capital')
        target = options.get('target')

        logger.info(f"Running backtest with arguments: instrument={instrument}, currency={currency}, capital={capital}, target={target}")

        if not instrument or not currency or capital is None or target is None:
            raise CommandError("One or more required arguments are missing or empty.")

        try:
            data = dbFuturesSimData()
            BASEDIR = os.getcwd()

            if os.name == 'posix':
                config_path = f"{BASEDIR}/private/run_backtest/config.yaml"
                template_path = f"{BASEDIR}/private/run_backtest/template.yaml"
            elif os.name == 'nt': 
                config_path = f"{BASEDIR}\\private\\run_backtest\\config.yaml"
                template_path = f"{BASEDIR}\\private\\run_backtest\\template.yaml"

            my_config = Config(config_path)
            my_config.instruments = instrument
            my_config.base_currency = currency
            my_config.notional_trading_capital = capital
            my_config.percentage_vol_target = target
            print(instrument)
            print(currency)
            print(capital)
            print(target)
            print(my_config.as_dict())

            system = System(
                [
                    Risk(),
                    accountForOptimisedStage(),
                    optimisedPositions(),
                    Portfolios(),
                    PositionSizing(),
                    myFuturesRawData(),
                    ForecastCombine(),
                    volAttenForecastScaleCap(),
                    Rules(),
                ],
                data,
                my_config,
            )

            profits = system.accounts.portfolio()

            parsed_result = profits.percent.stats()

            sysdiag = systemDiag(system)
            save_config_result = sysdiag.output_config_with_estimated_parameters(attr_names=[
                'forecast_scalars',
                'forecast_weights',
                'forecast_div_multiplier',
                'forecast_mapping',
                'instrument_weights',
                'instrument_div_multiplier'
            ])

            my_config = Config(template_path)
            print(save_config_result)
            my_config._create_config_from_dict(save_config_result)
            #print(my_config.as_dict())

            system = System(
                [
                    Risk(),
                    accountForOptimisedStage(),
                    optimisedPositions(),
                    Portfolios(),
                    PositionSizing(),
                    myFuturesRawData(),
                    ForecastCombine(),
                    volAttenForecastScaleCap(),
                    Rules(),
                ],
                data,
                my_config,
            )

            profits = system.accounts.portfolio()

            parsed_result = profits.percent.stats()

            logger.info(f"Parsed result: {parsed_result}")

            # Проверяем результаты на пустоту
            if not parsed_result or not parsed_result[0] or len(parsed_result[0]) < 21:
                raise CommandError("Parsed result is empty, invalid, or does not contain sufficient data.")

            for stat in parsed_result[0]:
                if not stat or len(stat) < 2:
                    raise CommandError("Parsed result contains invalid data.")

            logger.info(f"Backtest results: {parsed_result}")

            backtest_result = BacktestResult2(
                instruments=instrument,
                min=float(parsed_result[0][0][1]),
                max=float(parsed_result[0][1][1]),
                median=float(parsed_result[0][2][1]),
                mean=float(parsed_result[0][3][1]),
                std=float(parsed_result[0][4][1]),
                skew=float(parsed_result[0][5][1]),
                ann_mean=float(parsed_result[0][6][1]),
                ann_std=float(parsed_result[0][7][1]),
                sharpe=float(parsed_result[0][8][1]),
                sortino=float(parsed_result[0][9][1]),
                avg_drawdown=float(parsed_result[0][10][1]),
                time_in_drawdown=float(parsed_result[0][11][1]),
                calmar=float(parsed_result[0][12][1]),
                avg_return_to_drawdown=float(parsed_result[0][13][1]),
                avg_loss=float(parsed_result[0][14][1]),
                avg_gain=float(parsed_result[0][15][1]),
                gaintolossratio=float(parsed_result[0][16][1]),
                profitfactor=float(parsed_result[0][17][1]),
                hitrate=float(parsed_result[0][18][1]),
                t_stat=float(parsed_result[0][19][1]),
                p_value=float(parsed_result[0][20][1]),
            )
            backtest_result.save()
            res = backtest_result.id
            #stats_id = json.dumps(res)

            buffered_positions = []
            for inst in instrument:
                position = system.accounts.get_buffered_position(inst, roundpositions=True)
                # Получение последнего значения без даты
                last_value = position.iloc[-1]
                buffered_position = {'instrument': inst, 'position': last_value}
                buffered_positions.append(buffered_position)
                
            #logger.info(f"buffered_positions: {buffered_positions}")
            #positions = json.dumps(buffered_positions)
            return json.dumps({'command': 'run_backtest', 'stats': res, 'positions': buffered_positions})

        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise CommandError(f"Error running backtest: {e} instrument={instrument}, currency={currency}, capital={capital}, target={target}")
