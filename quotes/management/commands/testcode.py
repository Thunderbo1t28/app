from django.core.management.base import BaseCommand
from backtest.sysproduction.data.prices import get_valid_instrument_code_from_user
from quotes.sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices

from quotes.sysinit.futures.contract_prices_from_csv_to_arctic import init_arctic_with_csv_futures_contract_prices
from quotes.sysinit.futures.rollcalendars_from_arcticprices_to_csv import build_and_write_roll_calendar



class Command(BaseCommand):
    help = 'Test'

    
    def handle(self, *args, **options):
        '''barchart_csv_config = ConfigCsvFuturesPrices(
            input_date_index_name="<DATE>",
            input_skiprows=0,
            input_skipfooter=0,
            input_date_format="%Y-%m-%d",
            input_column_mapping=dict(
                OPEN="<OPEN>", HIGH="<HIGH>", LOW="<LOW>", FINAL="<CLOSE>", VOLUME="<VOL>"
            ),
        )
        datapath = "E:\\OneDrive\\Documents\\code\\djangosystemtrade\\app\\downloadData"
        data = init_arctic_with_csv_futures_contract_prices(datapath, csv_config=barchart_csv_config)'''
        #ewmac.tail(5)
        instrument_code = get_valid_instrument_code_from_user(source="single")
        ## MODIFY DATAPATH IF REQUIRED
        # build_and_write_roll_calendar(instrument_code, output_datapath=arg_not_supplied)
        build_and_write_roll_calendar(instrument_code, output_datapath="E:\\OneDrive\\Documents\\code\\djangosystemtrade\\app\\data\\futures\\roll_calendars_csv")
        #print(data)
        #multiple_prices = sim_data.get_multiple_prices_from_start_date(instrument_code, start_date)
        #spread_cost = sim_data.get_spread_cost(instrument_code)
        #backadjusted_prices = sim_data.get_backadjusted_futures_price(instrument_code)
        #instrument_meta_data = sim_data.get_instrument_meta_data(instrument_code)
        #roll_parameters = sim_data.get_roll_parameters(instrument_code)
        #instrument_with_meta_data = sim_data.get_instrument_object_with_meta_data(instrument_code)
        #raw_carry_data = sim_data.get_instrument_raw_carry_data(instrument_code)
        #current_forward_price_data = sim_data.get_current_and_forward_price_data(instrument_code)
        
        # Выведите результаты в консоль или сделайте что-то еще
        self.stdout.write(self.style.SUCCESS('Successfully'))
        

