import os
from django.core.management.base import BaseCommand
from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysproduction.data.prices import get_valid_instrument_code_from_user
from sysproduction.interactive_controls import interactive_controls
from sysproduction.interactive_diagnostics import interactive_diagnostics
from sysproduction.interactive_manual_check_fx_prices import interactive_manual_check_fx_prices
from sysproduction.interactive_order_stack import interactive_order_stack
from sysproduction.interactive_update_capital_manual import interactive_update_capital_manual
from sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from sysdata.arctic.arctic_spotfx_prices import arcticFxPricesData
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysdata.csv.csv_spot_fx import csvFxPricesData
from sysdata.data_blob import dataBlob
from sysinit.futures.adjustedprices_from_mongo_multiple_to_mongo import process_adjusted_prices_all_instruments

from sysinit.futures.contract_prices_from_csv_to_arctic import init_arctic_with_csv_futures_contract_prices, init_arctic_with_csv_futures_contract_prices_for_code
from sysinit.futures.multipleprices_from_arcticprices_and_csv_calendars_to_arctic import process_multiple_prices_all_instruments, process_multiple_prices_single_instrument
from sysinit.futures.repocsv_spread_costs import copy_spread_costs_from_csv_to_mongo
from sysinit.futures.rollcalendars_from_arcticprices_to_csv import build_and_write_roll_calendar
from sysproduction.interactive_update_roll_status import interactive_update_roll_status
from sysproduction.run_backups import run_backups
from sysproduction.run_capital_update import run_capital_update
from sysproduction.run_cleaners import run_cleaners
from sysproduction.run_reports import run_reports
from sysproduction.run_stack_handler import run_stack_handler
from sysproduction.run_strategy_order_generator import run_strategy_order_generator
from sysproduction.run_systems import run_systems
from sysproduction.update_sampled_contracts import update_sampled_contracts
from sysproduction.update_strategy_capital import update_strategy_capital
from sysproduction.update_total_capital import update_total_capital



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
        datapath = BASEDIR + "/downloadData"
        csv_multiple_data_path = f"{BASEDIR}\\data\\futures\\multiple_prices_csv"
        csv_roll_data_path = f"{BASEDIR}\\data\\futures\\roll_calendars_csv"


        #data = init_arctic_with_csv_futures_contract_prices(datapath, csv_config=barchart_csv_config)


        '''init_arctic_with_csv_futures_contract_prices_for_code(
            'AUDU', datapath, csv_config=barchart_csv_config
        )'''


        '''process_multiple_prices_single_instrument(
            instrument_code='AUDU',
            csv_multiple_data_path=csv_multiple_data_path,
            csv_roll_data_path=csv_roll_data_path,
            ADD_TO_ARCTIC=True,
            ADD_TO_CSV=True,
        )'''

        # '1MFR', 'AED', 'AFKS', 'AFLT', 'ALRS', 'AUDU', 'BANE', 'BELU', 'BR', 'BSPB', 'CBOM', 'CHMF', 'CNI', 'CNY', 'Co', 'DAX', 'ED', 'EJPY', 'Eu', 'FIVE', 'FLOT', 'FNI', 'GAZR', 'GBPU', 'GMKN', 'GOLD', 'HANG', 'HKD','HOME', 'HYDR', 'INR', 'ISKJ', 'KMAZ', 'KZT', 'LKOH', 'MAGN', 'MGNT', 'MIX', 'MMI', 'MOEX', 'MTLR', 'MTSI', 'MVID', 'MXI', 'NASD', 'NG', 'NIKK', 'NLMK', 'NOTK','OGI', 'OZON', 'PHOR', 'PIKK', 'PLD', 'PLT', 'PLZL', 'POLY', 'POSI', 'RGBI', 'ROSN', 'RTKM', 'RTS', 'RTSM', 'RUAL','RUON', 'SBPR', 'SBRF', 'SGZH', 'SIBN', 'SILV', 'SMLT', 'SNGP', 'SNGR','SPBE', 'SPYF', 'STOX', 'SUGAR','TATN', 'TRY', 'UCAD', 'UCHF', 'UCNY', 'UJPY', 'UTRY', 'VKCO', 'WHEAT', 'WUSH', 'YNDF'
        # 'ALMN','AMD', 'ASTR','Nl','RVI', 'SOFL','SUGR','TCSI', 'TRNF', ECAD, VTBR, Zn, 'IRAO', EGBP, 'EJPY', 'MMI', 'UTRY', 'RUON'
        #instrument_code = get_valid_instrument_code_from_user(source="single")
        ## MODIFY DATAPATH IF REQUIRED
        # build_and_write_roll_calendar(instrument_code, output_datapath=arg_not_supplied)
        '''instruments_list = ['UCAD', ] #'AUDU', 'FEES','TRNF','IRAO','Si','VTBR', '1MFR', 'AED', 'AFKS', 'AFLT', 'ALRS', 'AUDU', 'BANE', 'BELU', 'BR', 'BSPB', 'CBOM', 'CHMF', 'CNI', 'CNY', 'Co', 'DAX', 'ED',  'Eu', 'FIVE', 'FLOT', 'FNI', 'GAZR', 'GBPU', 'GMKN', 'GOLD', 'HANG', 'HKD','HOME', 'HYDR', 'INR', 'ISKJ', 'KMAZ', 'KZT', 'LKOH', 'MAGN', 'MGNT', 'MIX', 'MMI', 'MOEX', 'MTLR', 'MTSI', 'MVID', 'MXI', 'NASD', 'NG', 'NIKK', 'NLMK', 'NOTK','OGI', 'OZON', 'PHOR', 'PIKK', 'PLD', 'PLT', 'PLZL', 'POLY', 'POSI', 'RGBI', 'ROSN', 'RTKM', 'RTS', 'RTSM', 'RUAL','RUON', 'SBPR', 'SBRF', 'SGZH', 'SIBN', 'SILV', 'SMLT', 'SNGP', 'SNGR','SPBE', 'SPYF', 'STOX', 'SUGAR','TATN', 'TRY', 'UCAD', 'UCHF', 'UCNY', 'UJPY', 'UTRY', 'VKCO', 'WHEAT', 'WUSH', 'YNDF']
        for instrument in instruments_list:
            build_and_write_roll_calendar(instrument, output_datapath=f"{BASEDIR}\\data\\futures\\roll_calendars_csv")'''
        


        

        # modify flags as required
        '''process_multiple_prices_all_instruments(
            csv_multiple_data_path=csv_multiple_data_path,
            csv_roll_data_path=csv_roll_data_path,
        )'''
        

        '''process_adjusted_prices_all_instruments(
            ADD_TO_ARCTIC=True, ADD_TO_CSV=True, csv_adj_data_path=f"{BASEDIR}\\data\\futures\\adjusted_prices_csv"
        )'''

        #copy_spread_costs_from_csv_to_mongo(dataBlob())


        '''arctic_fx_prices = arcticFxPricesData()
        csv_fx_prices = csvFxPricesData()

        currency_code = input("Currency code? <return for ALL currencies> ")
        if currency_code == "":
            list_of_ccy_codes = csv_fx_prices.get_list_of_fxcodes()
        else:
            list_of_ccy_codes = [currency_code]

        for currency_code in list_of_ccy_codes:
            fx_prices = csv_fx_prices.get_fx_prices(currency_code)
            print(fx_prices)

            arctic_fx_prices.add_fx_prices(
                currency_code, fx_prices, ignore_duplication=True
            )'''




        #sim_data = dbFuturesSimData()
        #print(sim_data.get_merged_prices_for_instrument(instrument_code="AFKS"))
        #multiple_prices = sim_data.get_multiple_prices_from_start_date(instrument_code, start_date)
        #spread_cost = sim_data.get_spread_cost(instrument_code)
        #backadjusted_prices = sim_data.get_backadjusted_futures_price(instrument_code="AFKS")
        #instrument_meta_data = sim_data.get_instrument_meta_data(instrument_code)
        #roll_parameters = sim_data.get_roll_parameters(instrument_code)
        #instrument_with_meta_data = sim_data.get_instrument_object_with_meta_data(instrument_code)
        #raw_carry_data = sim_data.get_instrument_raw_carry_data(instrument_code="AFKS")
        #current_forward_price_data = sim_data.get_current_and_forward_price_data(instrument_code)
        #print(backadjusted_prices)

        
        #update_capital_pd_df_for_strategy()
        #interactive_update_capital_manual()
        #run_capital_update()
        #run_systems()
        #update_total_capital()
        #update_strategy_capital()
        #run_strategy_order_generator()
        #interactive_controls()
        #interactive_update_roll_status()
        #interactive_diagnostics()
        #interactive_manual_check_fx_prices()
        #interactive_manual_check_historical_prices()
        #update_sampled_contracts()
        #interactive_order_stack()
        #run_backups()
        #run_stack_handler()
        #run_cleaners()
        #run_reports()
        # Выведите результаты в консоль или сделайте что-то еще
        self.stdout.write(self.style.SUCCESS('Successfully'))
        

