from itertools import combinations
import json
from django.core.management.base import BaseCommand
import yaml
from backtest.models import BacktestResult
from systems.attenuate_vol.vol_attenuation_forecast_scale_cap import volAttenForecastScaleCap
from systems.provided.dynamic_small_system_optimise.accounts_stage import accountForOptimisedStage
from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import optimisedPositions
from systems.provided.rob_system.rawdata import myFuturesRawData
from systems.risk import Risk
from systems.forecasting import Rules
from systems.basesystem import System
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
        data = djangoFuturesSimData()
        
        my_config = Config("/Users/kairsabiev/code/proj1/app/private/autotest/config.yaml")
        # Получение аргументов из командной строки по их именам
        
        #config = MyConfigModel.objects.get(id=config_id)
        # Создание объекта Config с полученными параметрами
        instruments = data.get_instrument_list()
        # Количество инструментов в комбинации
        num_instruments_in_combination = 30

        # Создание списка всех возможных комбинаций инструментов заданной длины
        possible_instrument_combinations = list(combinations(instruments, num_instruments_in_combination))
        
        best_sharpe = -float('inf')
        best_instruments = []

        # Перебор всех возможных комбинаций инструментов
        for instruments_combination in possible_instrument_combinations:
        
            my_config.instruments = instruments_combination
            #print(initial_instruments_list)
            #my_config.instruments = ["Si", "BR", "GOLD", "NG", "Eu", "MXI", "MOEX", "ALRS",
                                    #"SILV", "SBRF", "GAZR", "ROSN", "MAGN", "SPYF", "NASD"]
            
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

            # Создание экземпляра BacktestResult и сохранение его в базе данных
            

            sysdiag = systemDiag(system)
            sysdiag.yaml_config_with_estimated_parameters('/Users/kairsabiev/code/proj1/app/private/autotest/result.yaml',
                                                        attr_names=['forecast_scalars',
                                                                            'forecast_weights',
                                                                            'forecast_div_multiplier',
                                                                            'forecast_mapping',
                                                                            'instrument_weights',
                                                                            'instrument_div_multiplier'])
            

            # Загрузка содержимого первого YAML файла
            with open('/Users/kairsabiev/code/proj1/app/private/autotest/template.yaml', 'r') as file1:
                data1 = yaml.safe_load(file1)

            # Загрузка содержимого второго YAML файла
            with open('/Users/kairsabiev/code/proj1/app/private/autotest/result.yaml', 'r') as file2:
                data2 = yaml.safe_load(file2)

            # Объединение данных из двух файлов
            combined_data = {**data1, **data2}

            # Запись объединенных данных в новый YAML файл
            with open('/Users/kairsabiev/code/proj1/app/private/autotest/combined.yaml', 'w') as outfile:
                yaml.dump(combined_data, outfile)
            
            my_config = Config("/Users/kairsabiev/code/proj1/app/private/autotest/combined.yaml")
            # Получение аргументов из командной строки по их именам
            
            #config = MyConfigModel.objects.get(id=config_id)
            # Создание объекта Config с полученными параметрами
            
            my_config.instruments = instruments_combination
            
            
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

            sharpe = profits.percent.stats()[0][8][1]  # Получение параметра sharpe из результатов
    
            # Сравнение с текущим лучшим значением
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_instruments = instruments_combination
        
        # Сохранение лучшей комбинации
        print("Best Sharpe:", best_sharpe)
        print("Best Instruments:", best_instruments)
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))
