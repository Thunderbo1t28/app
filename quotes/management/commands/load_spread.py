from django.core.management.base import BaseCommand
from quotes.models import Instrument, RollCalendar, SpreadCosts, Quote
import requests
import pandas as pd
from django.utils import timezone

MOEX_API_URL = "https://iss.moex.com/iss/engines/futures/markets/forts/securities.json"



class Command(BaseCommand):
    help = 'Load available instruments into the database'

    def handle(self, *args, **options):

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
            
            # Находим ближайший current_contract на последнюю дату
            last_roll_calendar_entry = RollCalendar.objects.filter(
                instrument__instrument=instrument_row.ASSETCODE,
                timestamp__lte="2024-01-18 00:00:00",
            ).order_by('-timestamp').first()
            #print(last_roll_calendar_entry.current_contract)
            if last_roll_calendar_entry:
                # Находим Quote по secid
                quote_obj = Quote.objects.filter(contract=last_roll_calendar_entry.current_contract).first()

                if quote_obj:
                    # Проверяем, существует ли уже SpreadCosts для данного инструмента и quote
                    existing_spread_costs = SpreadCosts.objects.filter(
                        instrument__instrument=instrument_row.ASSETCODE,
                    )

                    if not existing_spread_costs.exists():
                        instrument_obj = Instrument.objects.get(instrument=instrument_row.ASSETCODE)

                        SpreadCosts.objects.create(
                            instrument=instrument_obj,
                            spreadcost=instrument_row.SPREAD,
                        )
                        print('Data loaded successfully')
