import os
from django.core.management.base import BaseCommand
from quotes.models import Instrument, RollCalendar, SpreadCosts, Quote
import requests
import pandas as pd
from django.utils import timezone
from sysdata.data_blob import dataBlob
from sysinit.futures.repocsv_spread_costs import copy_spread_costs_from_csv_to_mongo

MOEX_API_URL = "https://iss.moex.com/iss/engines/futures/markets/forts/securities.json"



class Command(BaseCommand):
    help = 'Load available instruments into the database'

    def handle(self, *args, **options):
        instrument = [
                                    'AED',
                                    'AFLT',
                                    'AFKS',
                                    'ALRS',
                                    'ALUM',
                                    'ASTR',
                                    'AUDU',
                                    'ALIBABA',
                                    'BAIDU',
                                    'BRM',
                                    'BANE',
                                    'BR',
                                    'BSPB',
                                    'UCAD',
                                    'COCOA',
                                    'COPPER',
                                    'UCHF',
                                    'CHMF',
                                    'CBOM',
                                    'CNY',
                                    'CNI',
                                    'DJ30',
                                    'DAX',
                                    'ED',
                                    'EJPY',
                                    'EM',
                                    'Eu',
                                    'FESH',
                                    'FLOT',
                                    'FNI',
                                    'FEES',
                                    'GOLD',
                                    'GMKN',
                                    'GL',
                                    'GBPU',
                                    'GAZR',
                                    'HKD',
                                    'HOME',
                                    'HANG',
                                    'HYDR',
                                    'INR',
                                    'IPO',
                                    'ISKJ',
                                    'UJPY',
                                    'KMAZ',
                                    'KZT',
                                    'LEAS',
                                    'LKOH',
                                    'MMI',
                                    'MTLR',
                                    'MOEX',
                                    'MAGN',
                                    'MXI',
                                    'MGNT',
                                    'MTSI',
                                    'MVID',
                                    'MIX',
                                    'NIKK',
                                    'NASD',
                                    'NICKEL',
                                    'NG',
                                    'NOTK',
                                    'NLMK',
                                    'NGM',
                                    'OGI',
                                    'PLD',
                                    'PHOR',
                                    'PIKK',
                                    'POSI',
                                    'PLT',
                                    'PLZL',
                                    'R2000',
                                    'RASP',
                                    'RGBI',
                                    'RTS',
                                    'RUAL',
                                    'RTSM',
                                    'ROSN',
                                    'RTKM',
                                    'RNFT',
                                    'SOFL',
                                    'SUGR',
                                    'SVCB',
                                    'SPBE',
                                    'SPYF',
                                    'SNGP',
                                    'SFIN',
                                    'Si',
                                    'SNGR',
                                    'SIBN',
                                    'SBPR',
                                    'SBRF',
                                    'SMLT',
                                    'SUGAR',
                                    'SILV',
                                    'STOX',
                                    'SGZH',
                                    'TCSI',
                                    'TRNF',
                                    'TATP',
                                    'TATN',
                                    'TRY',
                                    'UCNY',
                                    'VTBR',
                                    'VKCO',
                                    'WHEAT',
                                    'WUSH',
                                    'YDEX',
                                    'ZINC',]
        response = requests.get(MOEX_API_URL)
        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")

        securities_data = data['securities']['data']
        securities_columns = data['securities']['columns']
        securities_df = pd.DataFrame(securities_data, columns=securities_columns)

        marketdata_data = data['marketdata']['data']
        marketdata_columns = data['marketdata']['columns']
        marketdata_df = pd.DataFrame(marketdata_data, columns=marketdata_columns)

        combined_df = pd.merge(securities_df, marketdata_df, how='inner', left_on=['SECID', 'BOARDID'], right_on=['SECID', 'BOARDID'])

        for instrument_row in combined_df.itertuples(index=False):
            
            print(instrument_row.ASSETCODE)
            # Проверяем, существует ли уже SpreadCosts для данного инструмента и quote
            existing_spread_costs = SpreadCosts.objects.filter(
                instrument__instrument=instrument_row.ASSETCODE,
            )

            if not existing_spread_costs.exists():
                if instrument_row.ASSETCODE  in instrument:
                    instrument_obj = Instrument.objects.get(instrument=instrument_row.ASSETCODE)
                    if instrument_obj:
                        SpreadCosts.objects.create(
                            instrument=instrument_obj,
                            spreadcost=instrument_row.SPREAD,
                        )
        BASEDIR = os.getcwd()
        spreads = [{}]
        instruments = Instrument.objects.all()
        for instrument in instruments:
            quotes = SpreadCosts.objects.filter(instrument=instrument)
            if quotes.exists():
                spreadcost_value = quotes[0].spreadcost
            else:
                spreadcost_value = None
            dict_spread = {'Instrument': str(instrument), 'SpreadCost': spreadcost_value}
            spreads.append(dict_spread)
        #print(spreads)    
        df = pd.DataFrame(spreads)
        # Создание каталога, если его нет
        directory = f"{BASEDIR}\\data\\futures\\csvconfig"
        os.makedirs(directory, exist_ok=True)
        
        # Сохранение в CSV-файл только если есть данные
        if not df.empty:
            df.to_csv(f'{directory}/spreadcosts.csv', index=False)
        

        copy_spread_costs_from_csv_to_mongo(dataBlob())
