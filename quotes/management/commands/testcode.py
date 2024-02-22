import os
from django.core.management.base import BaseCommand
from backtest.sysproduction.data.prices import get_valid_instrument_code_from_user
from quotes.sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from quotes.sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices

from quotes.sysinit.futures.contract_prices_from_csv_to_arctic import init_arctic_with_csv_futures_contract_prices
from quotes.sysinit.futures.multipleprices_from_arcticprices_and_csv_calendars_to_arctic import process_multiple_prices_all_instruments
from quotes.sysinit.futures.rollcalendars_from_arcticprices_to_csv import build_and_write_roll_calendar



class Command(BaseCommand):
    help = 'Test'

    
    def handle(self, *args, **options):
        barchart_csv_config = ConfigCsvFuturesPrices(
            input_date_index_name="<DATE>",
            input_skiprows=0,
            input_skipfooter=0,
            input_date_format="%Y-%m-%d %H:%M:%S",
            input_column_mapping=dict(
                OPEN="<OPEN>", HIGH="<HIGH>", LOW="<LOW>", FINAL="<CLOSE>", VOLUME="<VOL>"
            ),
        )
        BASEDIR = os.getcwd()



        print(BASEDIR)
        '''datapath = BASEDIR + "/downloadData"
        data = init_arctic_with_csv_futures_contract_prices(datapath, csv_config=barchart_csv_config)'''


        # '1MFR', 'AED', 'AFKS', 'AFLT', 'ALRS', 'AUDU', 'BANE', 'BELU', 'BR', 'BSPB', 'CBOM', 'CHMF', 'CNI', 'CNY', 'Co', 'DAX', 'ED', 'EJPY', 'Eu', 'FIVE', 'FLOT', 'FNI', 'GAZR', 'GBPU', 'GMKN', 'GOLD', 'HANG', 'HKD','HOME', 'HYDR', 'INR', 'ISKJ', 'KMAZ', 'KZT', 'LKOH', 'MAGN', 'MGNT', 'MIX', 'MMI', 'MOEX', 'MTLR', 'MTSI', 'MVID', 'MXI', 'NASD', 'NG', 'NIKK', 'NLMK', 'NOTK','OGI', 'OZON', 'PHOR', 'PIKK', 'PLD', 'PLT', 'PLZL', 'POLY', 'POSI', 'RGBI', 'ROSN', 'RTKM', 'RTS', 'RTSM', 'RUAL','RUON', 'SBPR', 'SBRF', 'SGZH', 'SIBN', 'SILV', 'SMLT', 'SNGP', 'SNGR','SPBE', 'SPYF', 'STOX', 'SUGAR','TATN', 'TRY', 'UCAD', 'UCHF', 'UCNY', 'UJPY', 'UTRY', 'VKCO', 'WHEAT', 'WUSH', 'YNDF'
        # 'ALMN','AMD', 'ASTR','Nl','RVI', 'SOFL','SUGR','TCSI', 'TRNF', ECAD, VTBR, Zn, IRAO
        #instrument_code = get_valid_instrument_code_from_user(source="single")
        ## MODIFY DATAPATH IF REQUIRED
        # build_and_write_roll_calendar(instrument_code, output_datapath=arg_not_supplied)
        '''instruments_list = ['VTBR']#'1MFR', 'AED', 'AFKS', 'AFLT', 'ALRS', 'AUDU', 'BANE', 'BELU', 'BR', 'BSPB', 'CBOM', 'CHMF', 'CNI', 'CNY', 'Co', 'DAX', 'ED', 'EJPY', 'Eu', 'FIVE', 'FLOT', 'FNI', 'GAZR', 'GBPU', 'GMKN', 'GOLD', 'HANG', 'HKD','HOME', 'HYDR', 'INR', 'ISKJ', 'KMAZ', 'KZT', 'LKOH', 'MAGN', 'MGNT', 'MIX', 'MMI', 'MOEX', 'MTLR', 'MTSI', 'MVID', 'MXI', 'NASD', 'NG', 'NIKK', 'NLMK', 'NOTK','OGI', 'OZON', 'PHOR', 'PIKK', 'PLD', 'PLT', 'PLZL', 'POLY', 'POSI', 'RGBI', 'ROSN', 'RTKM', 'RTS', 'RTSM', 'RUAL','RUON', 'SBPR', 'SBRF', 'SGZH', 'SIBN', 'SILV', 'SMLT', 'SNGP', 'SNGR','SPBE', 'SPYF', 'STOX', 'SUGAR','TATN', 'TRY', 'UCAD', 'UCHF', 'UCNY', 'UJPY', 'UTRY', 'VKCO', 'WHEAT', 'WUSH', 'YNDF']
        for instrument in instruments_list:
            build_and_write_roll_calendar(instrument, output_datapath=f"{BASEDIR}\\data\\futures\\roll_calendars_csv")'''
        


        '''csv_multiple_data_path = f"{BASEDIR}\\data\\futures\\multiple_prices_csv"

        # only change if you have written the files elsewhere
        csv_roll_data_path = f"{BASEDIR}\\data\\futures\\roll_calendars_csv"

        # modify flags as required
        process_multiple_prices_all_instruments(
            csv_multiple_data_path=csv_multiple_data_path,
            csv_roll_data_path=csv_roll_data_path,
        )'''


        '''sim_data = arcticFuturesContractPriceData()
        print(sim_data.get_merged_prices_for_instrument(instrument_code="AFKS"))'''
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
        

