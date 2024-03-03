#from sysdata.base_data import baseData
import pandas as pd
from sysdata.futures.adjusted_prices import futuresAdjustedPricesData
from sysobjects.adjusted_prices import futuresAdjustedPrices
from quotes.models import AdjustedPrice, Instrument  # Замените "your_app" на имя вашего приложения Django

class djangoFuturesAdjustedPricesData(futuresAdjustedPricesData):
    def _add_adjusted_prices_without_checking_for_existing_entry(
        self, instrument_code: str, adjusted_price_data: futuresAdjustedPrices
    ):
        instrument = Instrument.objects.get(instrument=instrument_code)
        for timestamp, price in adjusted_price_data.items():
            AdjustedPrice.objects.create(
                instrument_id=instrument,
                timestamp=timestamp,
                price=price
            )

    def get_list_of_instruments(self) -> list:
        #instrument_ids = AdjustedPrice.objects.values_list('instrument_id', flat=True).distinct()
        #instruments = Instrument.objects.filter(id__in=instrument_ids)
        instruments = Instrument.objects.all()
        return list(instruments.values_list('instrument', flat=True))

    def _delete_adjusted_prices_without_any_warning_be_careful(
        self, instrument_code: str
    ):
        instrument = Instrument.objects.get(instrument=instrument_code)
        AdjustedPrice.objects.filter(instrument_id=instrument).delete()

    def _get_adjusted_prices_without_checking(
        self, instrument_code: str
    ) -> futuresAdjustedPrices:
        instrument = Instrument.objects.get(instrument=instrument_code)
        #adjusted_prices = futuresAdjustedPrices()
        prices = AdjustedPrice.objects.filter(instrument=instrument).order_by('timestamp')
        adjusted_prices_df = pd.DataFrame.from_records(prices.values())
        adjusted_prices_df.set_index("timestamp", inplace=True)
        adjusted_prices_df.index = adjusted_prices_df.index.tz_localize(None)
        adjusted_prices_df = adjusted_prices_df['price']
        
        return futuresAdjustedPrices(adjusted_prices_df)
