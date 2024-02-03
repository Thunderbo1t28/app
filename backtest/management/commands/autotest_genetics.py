from django.core.management.base import BaseCommand
import yaml
from backtest.systems.attenuate_vol.vol_attenuation_forecast_scale_cap import volAttenForecastScaleCap
from backtest.systems.basesystem import System
from backtest.systems.diagoutput import systemDiag
from backtest.systems.forecast_combine import ForecastCombine
from backtest.systems.forecasting import Rules
from backtest.systems.portfolio import Portfolios
from backtest.systems.positionsizing import PositionSizing
from backtest.systems.provided.dynamic_small_system_optimise.accounts_stage import accountForOptimisedStage
from backtest.systems.provided.dynamic_small_system_optimise.optimised_positions_stage import optimisedPositions
from backtest.systems.provided.rob_system.rawdata import myFuturesRawData
from backtest.systems.risk import Risk
from deap import base, creator, tools, algorithms
import random
from django.core.management import call_command
from quotes.sysdata.config.configdata import Config

from quotes.sysdata.sim.django_futures_sim_data import djangoFuturesSimData

# Определение класса для оптимизации параметра Sharpe
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)



class Command(BaseCommand):
    help = 'Run genetic algorithm for autotest'

    def handle(self, *args, **options):
        # Настройка генетического алгоритма
        # Настройка генетического алгоритма
        data = djangoFuturesSimData()
        all_instruments = data.get_instrument_list()
        toolbox = base.Toolbox()
        toolbox.register("attr_bool", random.randint, 0, 1)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=len(all_instruments))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        
        # Функция для оценки индивида (комбинации инструментов) по параметру Sharpe
        def evaluate(individual):
            instruments = [all_instruments[i] for i, gene in enumerate(individual) if gene]
            my_config = Config("/Users/kairsabiev/code/proj1/app/private/autotest/config.yaml")
            my_config.instruments = instruments
            system = System([
                Risk(),
                accountForOptimisedStage(),
                optimisedPositions(),
                Portfolios(),
                PositionSizing(),
                myFuturesRawData(),
                ForecastCombine(),
                volAttenForecastScaleCap(),
                Rules(),
            ], data, my_config)
            profits = system.accounts.portfolio()
            parsed_result = profits.percent.stats()

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
            
            # Создание объекта Config с полученными параметрами
            my_config.instruments = instruments
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
            sharpe = float(profits.percent.stats()[0][8][1])
            return (sharpe,)
        toolbox.register("evaluate", evaluate)
        # Создание начальной популяции
        population = toolbox.population(n=100)

        # Запуск генетического алгоритма
        algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, verbose=True)

        # Получение лучшего индивида (комбинации инструментов)
        best_individual = tools.selBest(population, k=1)[0]

        # Оценка лучшего индивида по параметру Sharpe
        best_sharpe = evaluate(best_individual)

        self.stdout.write(self.style.SUCCESS(f'Best Sharpe: {best_sharpe}'))
        self.stdout.write(self.style.SUCCESS(f'Best Individual: {best_individual}'))