import json
import os
from django.core.management.base import BaseCommand
from django.utils import encoding
import yaml
from backtest.models import BacktestResult, BacktestResult2
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
        data = dbFuturesSimData()
        BASEDIR = os.getcwd()
        my_config = Config(f"{BASEDIR}\\private\\test_single\\config_equal.yaml")
        # Получение аргументов из командной строки по их именам
        
        #config = MyConfigModel.objects.get(id=config_id)
        # Создание объекта Config с полученными параметрами
        instruments = ['MGNT', 'NG', 'PLZL', 'ALRS', 'AFKS', 'VTBR', 'Eu', 'SNGR', 'Si', 'GMKN', 'SNGP', 'GAZR', 'RTKM', 'MXI', 'ROSN', 'SBPR', 'SBRF', 'LKOH', 'SILV', 'MOEX', 'PLT', 'HYDR', 'ED', 'GBPU', 'AUDU']
        print(instruments)
        
            
        my_config.instruments = (instruments)
        
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

        # Создание экземпляра BacktestResult и сохранение его в базе данных
        

        sysdiag = systemDiag(system)
        
        
        # Определение базового каталога
        if os.name == 'posix':  # для Unix-подобных систем (например, macOS, Linux)
            sysdiag.yaml_config_with_estimated_parameters(f"{BASEDIR}/private/test_single/result_equal.yaml",
                                                    attr_names=['forecast_scalars',
                                                                        'forecast_weights',
                                                                        'forecast_div_multiplier',
                                                                        'forecast_mapping',
                                                                        'instrument_weights',
                                                                        'instrument_div_multiplier'])
            # Загрузка содержимого первого YAML файла
            with open(f"{BASEDIR}/private/test_single/template_equal.yaml", 'r') as file1:
                data1 = yaml.safe_load(file1)

            # Загрузка содержимого второго YAML файла
            with open(f'{BASEDIR}/private/test_single/result_equal.yaml', 'r') as file2:
                data2 = yaml.safe_load(file2)

            # Объединение данных из двух файлов
            combined_data = {**data1, **data2}

            # Запись объединенных данных в новый YAML файл
            with open(f'{BASEDIR}/private/test_single/combined_equal.yaml', 'w') as outfile:
                yaml.dump(combined_data, outfile)
        elif os.name == 'nt':   # для Windows
            sysdiag.yaml_config_with_estimated_parameters(f"{BASEDIR}\\private\\test_single\\result.yaml",
                                                    attr_names=['forecast_scalars',
                                                                        'forecast_weights',
                                                                        'forecast_div_multiplier',
                                                                        'forecast_mapping',
                                                                        'instrument_weights',
                                                                        'instrument_div_multiplier'])
            with open(f"{BASEDIR}\\private\\test_single\\template.yaml", 'r') as file1:
                data1 = yaml.safe_load(file1)

            # Загрузка содержимого второго YAML файла
            with open(f'{BASEDIR}\\private\\test_single\\result.yaml', 'r') as file2:
                data2 = yaml.safe_load(file2)

            # Объединение данных из двух файлов
            combined_data = {**data1, **data2}

            # Запись объединенных данных в новый YAML файл
            with open(f'{BASEDIR}\\private\\test_single\\combined.yaml', 'w') as outfile:
                yaml.dump(combined_data, outfile)
        else:
            raise NotImplementedError("Unsupported operating system")
        
        
        my_config = Config(f"{BASEDIR}\\private\\test_single\\combined_equal.yaml")
        # Получение аргументов из командной строки по их именам
        
        #config = MyConfigModel.objects.get(id=config_id)
        # Создание объекта Config с полученными параметрами
        
        my_config.instruments = (instruments)
        
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
        get_weights = system.portfolio.get_instrument_weights()
        #get_weights.to_csv(f"{BASEDIR}\\private\\test_single\\instrument_weights.csv", encoding="utf-8")
        backtest_result = BacktestResult2(
            instruments = instruments,
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
        self.stdout.write(self.style.SUCCESS('Successfully Becktest Single Equal.'))
