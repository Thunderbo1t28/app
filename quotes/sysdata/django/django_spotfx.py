import pandas as pd
from quotes.models import FxPriceData
from quotes.sysdata.fx.spotfx import fxPricesData
from quotes.sysobjects.spot_fx_prices import fxPrices  # Импорт модели данных Django

class DjangoFxPricesData(fxPricesData):
    """
    Class to read / write fx prices using Django ORM
    """

    def __init__(self):
        super().__init__()

    def get_list_of_fxcodes(self) -> list:
        # Получаем уникальные коды валют из базы данных Django
        return FxPriceData.objects.values_list("currency", flat=True).distinct()

    def _get_fx_prices_without_checking(self, currency_code: str) -> fxPrices:
        # Получаем данные из базы данных Django для указанного кода валюты
        fx_data = FxPriceData.objects.filter(currency=currency_code).values_list("timestamp", "price").order_by('timestamp')
        if not fx_data:
            return fxPrices.create_empty()  # Если данные отсутствуют, возвращаем пустой объект fxPrices

        # Создаем DataFrame с данными
        df = pd.DataFrame(fx_data, columns=["timestamp", "price"])
        df.set_index("timestamp", inplace=True)
        df.index = df.index.tz_localize(None)

        df.index = pd.to_datetime(df.index)
        series_from_df = df.squeeze()
        #df = df['price']
        # Создаем объект fxPrices из DataFrame
        fx_prices = fxPrices(series_from_df)
        return fx_prices

    def _delete_fx_prices_without_any_warning_be_careful(self, currency_code: str):
        # Удаляем данные из базы данных Django для указанного кода валюты
        FxPriceData.objects.filter(currency=currency_code).delete()
        #self.log.debug(f"Deleted FX prices for {currency_code}")

    def _add_fx_prices_without_checking_for_existing_entry(
        self, currency_code: str, fx_price_data: fxPrices
    ):
        # Создаем записи в базе данных Django на основе данных объекта fxPrices
        for timestamp, price in fx_price_data.items():
            FxPriceData.objects.create(currency=currency_code, timestamp=timestamp, price=price)
        #self.log.debug(f"Added FX prices for {currency_code}")
