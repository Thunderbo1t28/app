from django.core.management.base import BaseCommand
import yaml
from backtest.models import BacktestResult, BacktestResult2
from systems.attenuate_vol.vol_attenuation_forecast_scale_cap import volAttenForecastScaleCap
from systems.basesystem import System
from systems.diagoutput import systemDiag
from systems.forecast_combine import ForecastCombine
from systems.forecasting import Rules
from systems.portfolio import Portfolios
from systems.positionsizing import PositionSizing
from systems.provided.dynamic_small_system_optimise.accounts_stage import accountForOptimisedStage
from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import optimisedPositions
from systems.provided.rob_system.rawdata import myFuturesRawData
from systems.risk import Risk
from deap import base, creator, tools, algorithms
import random
from django.core.management import call_command
from sysdata.config.configdata import Config

from sysdata.sim.django_futures_sim_data import djangoFuturesSimData

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
            my_config = Config("E:\\OneDrive\\Documents\\code\\djangosystemtrade\\app\\private\\autotest\\config.yaml")
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
            sysdiag.yaml_config_with_estimated_parameters('E:\\OneDrive\\Documents\\code\\djangosystemtrade\\app\\private\\autotest\\result.yaml',
                                                        attr_names=['forecast_scalars',
                                                                            'forecast_weights',
                                                                            'forecast_div_multiplier',
                                                                            'forecast_mapping',
                                                                            'instrument_weights',
                                                                            'instrument_div_multiplier'])
            

            # Загрузка содержимого первого YAML файла
            with open('E:\\OneDrive\\Documents\\code\\djangosystemtrade\\app\\private\\autotest\\template.yaml', 'r') as file1:
                data1 = yaml.safe_load(file1)

            # Загрузка содержимого второго YAML файла
            with open('E:\\OneDrive\\Documents\\code\\djangosystemtrade\\app\\private\\autotest\\result.yaml', 'r') as file2:
                data2 = yaml.safe_load(file2)

            # Объединение данных из двух файлов
            combined_data = {**data1, **data2}

            # Запись объединенных данных в новый YAML файл
            with open('E:\\OneDrive\\Documents\\code\\djangosystemtrade\\app\\private\\autotest\\combined.yaml', 'w') as outfile:
                yaml.dump(combined_data, outfile)
            
            my_config = Config("E:\\OneDrive\\Documents\\code\\djangosystemtrade\\app\\private\\autotest\\combined.yaml")
            
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
            parsed_result = profits.percent.stats()


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