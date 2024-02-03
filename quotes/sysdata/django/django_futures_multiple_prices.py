import pandas as pd
from quotes.sysdata.base_data import baseData
from quotes.models import Instrument, MultiplePriceData
from quotes.sysdata.futures.multiple_prices import futuresMultiplePricesData  # Замените "your_app" на имя вашего приложения Django
from quotes.sysobjects.multiple_prices import futuresMultiplePrices
from quotes.sysobjects.dict_of_named_futures_per_contract_prices import (
        contract_name_from_column_name,
        price_name,
        carry_name,
        forward_name
    )

class djangoFuturesMultiplePricesData(futuresMultiplePricesData):
    """
    Read and write data class to get multiple prices for a specific future using Django ORM.

    We'd inherit from this class for a specific implementation.
    """

    def __repr__(self):
        return "DjangoFuturesMultiplePricesData base class - DO NOT USE"

    def _add_multiple_prices_without_checking_for_existing_entry(
        self, instrument_code: str, multiple_price_data: futuresMultiplePrices
    ):
        instrument = Instrument.objects.get(instrument=instrument_code)
        for datetime, price_data in multiple_price_data.items():
            MultiplePriceData.objects.create(
                instrument=instrument,
                datetime=datetime,
                carry=price_data['carry'],
                carry_contract=price_data['carry_contract'],
                price=price_data['price'],
                price_contract=price_data['price_contract'],
                forward=price_data['forward'],
                forward_contract=price_data['forward_contract']
            )

    def get_list_of_instruments(self) -> list:
        #instrument_ids = MultiplePriceData.objects.values_list('instrument_id', flat=True).distinct()
        #instruments = Instrument.objects.filter(id__in=instrument_ids)
        instruments = Instrument.objects.all()
        return list(instruments.values_list('instrument', flat=True))
        #return list(MultiplePriceData.objects.values_list('instrument', flat=True).distinct())

    def _get_multiple_prices_without_checking(
        self, instrument_code: str
    ) -> futuresMultiplePrices:
        

        instrument = Instrument.objects.get(instrument=instrument_code)
        prices_data = MultiplePriceData.objects.filter(
            instrument=instrument).order_by('datetime')

        # Convert Django QuerySet to a DataFrame
        prices_df = pd.DataFrame.from_records(prices_data.values())
        prices_df.set_index("datetime", inplace=True)
        prices_df.index = prices_df.index.tz_localize(None)
        
        # Assuming your model fields match the expected column names
        prices_df = prices_df.rename(columns={
            'carry': carry_name,
            'carry_contract': contract_name_from_column_name(carry_name),
            'price': price_name,
            'price_contract': contract_name_from_column_name(price_name),
            'forward': forward_name,
            'forward_contract': contract_name_from_column_name(forward_name)
        })
        prices_df = prices_df[[carry_name, contract_name_from_column_name(carry_name), 
                                price_name, contract_name_from_column_name(price_name), 
                                forward_name, contract_name_from_column_name(forward_name)]]
        #prices_df.set_index("datetime", inplace=True)
        #prices_df.index = prices_df.index.tz_localize(None)
        #print(data)
        return futuresMultiplePrices(prices_df)

    def _delete_multiple_prices_without_any_warning_be_careful(
        self, instrument_code: str
    ):
        instrument = Instrument.objects.get(instrument=instrument_code)
        MultiplePriceData.objects.filter(instrument=instrument).delete()
