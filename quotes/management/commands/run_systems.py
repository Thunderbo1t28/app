import os
from django.core.management.base import BaseCommand
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysinit.futures.adjustedprices_from_mongo_multiple_to_mongo import process_adjusted_prices_all_instruments
from sysproduction.interactive_order_stack import interactive_order_stack
from sysproduction.run_strategy_order_generator import run_strategy_order_generator
from sysproduction.run_systems import run_systems



class Command(BaseCommand):
    help = 'Test'

    
    def handle(self, *args, **options):

        run_systems()
        run_strategy_order_generator()
        #interactive_order_stack()
        

        # Выведите результаты в консоль или сделайте что-то еще
        self.stdout.write(self.style.SUCCESS('Successfully'))
        

