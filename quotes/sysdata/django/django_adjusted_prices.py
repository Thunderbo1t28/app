#from quotes.sysdata.base_data import baseData
from quotes.sysdata.futures.adjusted_prices import futuresAdjustedPricesData
from quotes.sysobjects.adjusted_prices import futuresAdjustedPrices
from quotes.models import AdjustedPrice  # Замените "your_app" на имя вашего приложения Django

class DjangoAdjustedPricesData(futuresAdjustedPricesData):
    def _add_adjusted_prices_without_checking_for_existing_entry(
        self, instrument_code: str, adjusted_price_data: futuresAdjustedPrices
    ):
        for timestamp, price in adjusted_price_data.items():
            AdjustedPrice.objects.create(
                instrument_id=instrument_code,
                timestamp=timestamp,
                price=price
            )

    def get_list_of_instruments(self) -> list:
        return list(AdjustedPrice.objects.values_list('instrument', flat=True).distinct())

    def _delete_adjusted_prices_without_any_warning_be_careful(
        self, instrument_code: str
    ):
        AdjustedPrice.objects.filter(instrument_id=instrument_code).delete()

    def _get_adjusted_prices_without_checking(
        self, instrument_code: str
    ) -> futuresAdjustedPrices:
        adjusted_prices = futuresAdjustedPrices()
        prices = AdjustedPrice.objects.filter(instrument_id=instrument_code)
        for price in prices:
            adjusted_prices[price.timestamp] = price.price
        return adjusted_prices
