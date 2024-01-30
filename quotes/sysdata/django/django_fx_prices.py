
from locale import currency

import pandas as pd
from quotes.models import FxPriceData
from quotes.sysdata.fx.spotfx import fxPricesData
from quotes.sysobjects.spot_fx_prices import fxPrices

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
        fx_price_data = FxPriceData.objects.filter(currency=code)
        #fx_prices_data = fxPrices.create_from_queryset(fx_price_instances)
        #print(fx_prices_data)
        fx_data = djangoFxPricesData()

        # Проходим по каждой записи и добавляем ее в объект fxPricesData
        for entry in fx_price_data:
            currency = entry.currency
            timestamp = entry.timestamp
            price = entry.price

            # Создаем DataFrame с данными
            data = pd.DataFrame({"timestamp": [timestamp], "price": [price]})
            data.set_index("timestamp", inplace=True)
            data.index = data.index.tz_localize(None)
            data.index = pd.to_datetime(data.index)
            series_from_df = data.squeeze()
            #data = data['price']
            # Добавляем данные в объект fxPricesData
            fx_data.add_fx_prices(currency, series_from_df)
        return fx_data

    def get_list_of_fxcodes(self):
        # Получение списка всех кодов из базы данных
        return list(FxPriceData.objects.values_list('currency', flat=True))
