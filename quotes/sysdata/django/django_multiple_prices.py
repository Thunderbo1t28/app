from quotes.sysdata.base_data import baseData
from quotes.models import MultiplePriceData
from quotes.sysdata.futures.multiple_prices import futuresMultiplePricesData  # Замените "your_app" на имя вашего приложения Django
from quotes.sysobjects.multiple_prices import futuresMultiplePrices

class DjangoFuturesMultiplePricesData(futuresMultiplePricesData):
    """
    Read and write data class to get multiple prices for a specific future using Django ORM.

    We'd inherit from this class for a specific implementation.
    """

    def __repr__(self):
        return "DjangoFuturesMultiplePricesData base class - DO NOT USE"

    def _add_multiple_prices_without_checking_for_existing_entry(
        self, instrument_code: str, multiple_price_data: futuresMultiplePrices
    ):
        for datetime, price_data in multiple_price_data.items():
            MultiplePriceData.objects.create(
                instrument=instrument_code,
                datetime=datetime,
                carry=price_data['carry'],
                carry_contract=price_data['carry_contract'],
                price=price_data['price'],
                price_contract=price_data['price_contract'],
                forward=price_data['forward'],
                forward_contract=price_data['forward_contract']
            )

    def get_list_of_instruments(self) -> list:
        return list(MultiplePriceData.objects.values_list('instrument', flat=True).distinct())

    def _get_multiple_prices_without_checking(
        self, instrument_code: str
    ) -> futuresMultiplePrices:
        multiple_prices = futuresMultiplePrices()
        price_data_queryset = MultiplePriceData.objects.filter(instrument=instrument_code)
        for price_data in price_data_queryset:
            multiple_prices[price_data.datetime] = {
                'carry': price_data.carry,
                'carry_contract': price_data.carry_contract,
                'price': price_data.price,
                'price_contract': price_data.price_contract,
                'forward': price_data.forward,
                'forward_contract': price_data.forward_contract,
            }
        return multiple_prices

    def _delete_multiple_prices_without_any_warning_be_careful(
        self, instrument_code: str
    ):
        MultiplePriceData.objects.filter(instrument=instrument_code).delete()
