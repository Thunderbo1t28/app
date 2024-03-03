
from locale import currency

import pandas as pd
from quotes.models import FxPriceData
from sysdata.fx.spotfx import fxPricesData
from sysobjects.spot_fx_prices import fxPrices

class djangoFxPricesData(fxPricesData):
    """
    Read and write data class to get FX prices using Django ORM.

    We'd inherit from this class for a specific implementation.
    """

    def __repr__(self):
        return "DjangoFxPricesData base class - DO NOT USE"

    def _add_fx_prices_without_checking_for_existing_entry(self, code, fx_price_data):
        # Создание записи в базе данных на основе переданного объекта fxPrices
        FxPriceData.objects.create(
            timestamp=fx_price_data.timestamp,
            exchange=fx_price_data.exchange,
            section=fx_price_data.section,
            instrument=fx_price_data.instrument,
            currency=fx_price_data.currency,
            price=fx_price_data.price
        )

    def _delete_fx_prices_without_any_warning_be_careful(self, code):
        # Удаление всех записей из базы данных с указанным кодом
        FxPriceData.objects.filter(instrument=code).delete()

    def _get_fx_prices_without_checking(self, code):
        # Получение всех записей из базы данных с указанным кодом и преобразование их в объект fxPrices
        fx_price_data = FxPriceData.objects.filter(currency=code).order_by("timestamp")

        # Создаем экземпляр класса fxPricesData
        fx_price_df = pd.DataFrame.from_records(fx_price_data.values())
        fx_price_df.set_index("timestamp", inplace=True)
        fx_price_df.index = fx_price_df.index.tz_localize(None)
        fx_price_df = fx_price_df['price']

        return fxPrices(fx_price_df)

    def get_list_of_fxcodes(self):
        # Получение списка всех кодов из базы данных
        return list(FxPriceData.objects.values_list('currency', flat=True))
