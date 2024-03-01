import json
import os
from django.core.management.base import BaseCommand
import yaml
from backtest.models import BacktestResult, BacktestResult2
from backtest.systems.attenuate_vol.vol_attenuation_forecast_scale_cap import volAttenForecastScaleCap
from backtest.systems.provided.dynamic_small_system_optimise.accounts_stage import accountForOptimisedStage
from backtest.systems.provided.dynamic_small_system_optimise.optimised_positions_stage import optimisedPositions
from backtest.systems.provided.rob_system.rawdata import myFuturesRawData
from backtest.systems.risk import Risk
from backtest.systems.forecasting import Rules
from backtest.systems.basesystem import System
from quotes.sysdata.sim.db_futures_sim_data import dbFuturesSimData
from quotes.sysdata.sim.django_futures_sim_data import djangoFuturesSimData
from quotes.sysdata.config.configdata import Config
from backtest.systems.forecast_combine import ForecastCombine
from backtest.systems.positionsizing import PositionSizing
from backtest.systems.portfolio import Portfolios
from backtest.systems.diagoutput import systemDiag


class Command(BaseCommand):
    help = 'Test EWMA Trading Rule using DjangoFuturesSimData'

    
    def handle(self, *args, **options):
        #callback_function = options['callback']
        #logging.info("Starting backtest_test command...")
        data = dbFuturesSimData()
        BASEDIR = os.getcwd()
        #my_config = Config(f"{BASEDIR}\\private\\test_single\\config.yaml")
        
        
        # Получение аргументов из командной строки по их именам
        
        #config = MyConfigModel.objects.get(id=config_id)
        # Создание объекта Config с полученными параметрами
        instruments = data.get_instrument_list()
        
        for instrument in instruments:
            print(instrument)
            my_config = Config(f"{BASEDIR}\\private\\autotest\\config.yaml")
            my_config.instruments = [instrument]
            
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
            print(my_config.instruments)
            profits = system.accounts.portfolio()
            parsed_result = profits.percent.stats()
            
            sysdiag = systemDiag(system)
            sysdiag.yaml_config_with_estimated_parameters(f'{BASEDIR}\\private\\autotest\\result.yaml',
                                                        attr_names=['forecast_scalars',
                                                                            'forecast_weights',
                                                                            'forecast_div_multiplier',
                                                                            'forecast_mapping',
                                                                            'instrument_weights',
                                                                            'instrument_div_multiplier'])
            

            # Загрузка содержимого первого YAML файла
            with open(f'{BASEDIR}\\private\\autotest\\template.yaml', 'r') as file1:
                data1 = yaml.safe_load(file1)

            # Загрузка содержимого второго YAML файла
            with open(f'{BASEDIR}\\private\\autotest\\result.yaml', 'r') as file2:
                data2 = yaml.safe_load(file2)

            # Объединение данных из двух файлов
            combined_data = {**data1, **data2}

            # Запись объединенных данных в новый YAML файл
            with open(f'{BASEDIR}\\private\\autotest\\combine.yaml', 'w') as outfile:
                yaml.dump(combined_data, outfile)
            
            my_config = Config(f"{BASEDIR}\\private\\autotest\\combine.yaml")
            # Получение аргументов из командной строки по их именам
            
            #config = MyConfigModel.objects.get(id=config_id)
            # Создание объекта Config с полученными параметрами
            
            my_config.instruments = [instrument]
            
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

            # Преобразование результатов в формат JSON
            metrics_json = json.dumps(profits.percent.stats())
            additional_info_json = json.dumps(profits.gross.percent.stats())

            parsed_result = profits.percent.stats()


            backtest_result = BacktestResult2(
                instruments = instrument,
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
            # Сохранение экземпляра в базе данных
            backtest_result.save()
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))
