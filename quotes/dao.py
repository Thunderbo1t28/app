from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F
import pandas as pd

from quotes.models import AdjustedPrice, FxPriceData, Instrument, MultiplePriceData, RollCalendar, SpreadCosts
from quotes.sysdata.futures.instruments import futuresInstrumentData
from quotes.sysobjects.adjusted_prices import futuresAdjustedPrices
from quotes.sysobjects.instruments import assetClassesAndInstruments
from quotes.sysobjects.spot_fx_prices import fxPrices

class DjangoFuturesSimData(object):
    def __repr__(self):
        return "DjangoFuturesSimData object with %d instruments" % len(
            self.get_instrument_list()
        )
    def get_instrument_list(self):
        instrument_list = Instrument.objects.values_list('instrument', flat=True).distinct()
        instrument_list_df = pd.DataFrame(instrument_list, columns=['instrument'])
        return list(instrument_list_df['instrument'])
    
    def _get_fx_data_from_start_date(
        self, currency1: str, currency2: str, start_date
    ):
        fx_code = currency1 + currency2
        data = FxPriceData.objects.filter(currency = fx_code).order_by('timestamp')
        data_df = pd.DataFrame.from_records(
                data.values("timestamp", "price")
            )
        data_df.set_index("timestamp", inplace=True)

        data_df = data_df['price']
        #data_df.index.name = "index"
        #data_df.name = ""
        #data_df = fxPricesData(data_df).get_fx_prices(fx_code=fx_code)
        data_after_start = data_df[start_date:]
        #print(data_after_start.all)

        return fxPrices(data_after_start)

    def get_instrument_asset_classes(self):
        all_instrument_data = self.get_all_instrument_data_as_df()
        asset_classes = all_instrument_data["asset_class"]
        asset_class_data = assetClassesAndInstruments.from_pd_series(asset_classes)

        return asset_class_data

    def get_all_instrument_data_as_df(self):
        #all_instrument_data = Instrument.objects.values_list('instrument', 'asset_class').distinct()
        #all_instrument_data_df = pd.DataFrame(all_instrument_data, columns=['instrument'])
        #all_instrument_data_df = futuresInstrumentData(all_instrument_data_df)
        # Получаем данные из базы данных Django для модели Instrument
        instrument_data = Instrument.objects.all().values()

        # Преобразуем полученные данные в DataFrame
        instrument_df = pd.DataFrame.from_records(instrument_data)

        # Устанавливаем столбец 'instrument' в качестве индекса
        instrument_df.set_index('instrument', inplace=True)

        instrument_list = self.get_instrument_list()
        #instrument_list.set_index('instrument', inplace=True)

        #all_instrument_data = instrument_df[
            #instrument_df.isin(instrument_list)
        #]
        all_instrument_data = instrument_df.loc[instrument_list]
        return all_instrument_data


    def get_multiple_prices_from_start_date(
        self, instrument_code: str, start_date
    ) :
        """
        Get multiple prices data from the start date for a given instrument.

        :param instrument_code: str
        :param start_date: datetime.datetime
        :return: futuresMultiplePrices
        """
        instrument = Instrument.objects.get(instrument=instrument_code)
        prices_data = MultiplePriceData.objects.filter(
            instrument=instrument, datetime__gte=start_date
        ).order_by('datetime')

        # Convert Django QuerySet to a DataFrame
        prices_df = pd.DataFrame.from_records(prices_data.values())

        # Assuming your model fields match the expected column names
        prices_df = prices_df.rename(columns={
            'carry_contract': carry_contract_name,
            'price': price_name,
            'price_contract': price_contract_name,
            'forward': forward_name,
            'forward_contract': forward_contract_name
        })

        return prices_df

    def get_spread_cost(self, instrument_code: str) -> float:
        """
        Get spread cost for a given instrument.

        :param instrument_code: str
        :return: float
        """
        instrument = Instrument.objects.get(instrument=instrument_code)
        cost_data = SpreadCosts.objects.get(instrument=instrument)

        return cost_data.spreadcost

    def get_backadjusted_futures_price(
        self, instrument_code: str
        ):
        """
        Get backadjusted futures price for a given instrument.

        :param instrument_code: str
        :return: futuresAdjustedPrices
        """
        try:
            # Получаем объект инструмента из базы данных
            instrument = Instrument.objects.get(instrument=instrument_code)
            
            # Получаем цены из базы данных для данного инструмента, упорядоченные по времени
            adjusted_prices_data = AdjustedPrice.objects.filter(instrument=instrument).order_by('timestamp')

            # Преобразуем QuerySet в DataFrame
            adjusted_prices_df = pd.DataFrame.from_records(adjusted_prices_data.values())

            # Возвращаем объект futuresAdjustedPrices, используя DataFrame
            return futuresAdjustedPrices(adjusted_prices_df)
        except ObjectDoesNotExist:
            raise ValueError("Instrument {} not found".format(instrument_code))

    def get_instrument_meta_data(
        self, instrument_code: str
    ):
        """
        Get meta data for a given instrument.

        :param instrument_code: str
        :return: futuresInstrumentWithMetaData
        """
        instrument = Instrument.objects.get(instrument=instrument_code)

        return instrument

    def get_roll_parameters(self, instrument_code: str):
        """
        Get roll parameters for a given instrument.

        :param instrument_code: str
        :return: rollParameters
        """
        instrument = Instrument.objects.get(instrument=instrument_code)
        roll_params_data = RollCalendar.objects.filter(
            instrument=instrument
        ).order_by('timestamp')

        # Convert Django QuerySet to a DataFrame
        roll_params_df = pd.DataFrame.from_records(roll_params_data.values())

        return roll_params_df

    def get_instrument_object_with_meta_data(
        self, instrument_code: str
    ):
        """
        Get data about an instrument as a futuresInstrumentWithMetaData.

        :param instrument_code: str
        :return: futuresInstrumentWithMetaData
        """
        instrument = Instrument.objects.get(instrument=instrument_code)

        return instrument
    def get_instrument_raw_carry_data(self, instrument_code: str) -> pd.DataFrame:
        """
        Возвращает pd.DataFrame с 4 столбцами: PRICE, CARRY, PRICE_CONTRACT, CARRY_CONTRACT.

        Эти данные специально необходимы для фьючерсной торговли.

        :param instrument_code: инструмент для получения данных по переносу
        :type instrument_code: str

        :returns: pd.DataFrame
        """

        instrument = Instrument.objects.get(instrument=instrument_code)
        all_price_data = MultiplePriceData.objects.filter(
            instrument=instrument
        ).order_by('datetime')

        # Преобразуем QuerySet Django в DataFrame
        carry_data_df = pd.DataFrame.from_records(all_price_data.values())

        # Переименовываем столбцы, если необходимо
        carry_data_df = carry_data_df.rename(columns={
            'carry_contract': carry_contract_name,
            'price': price_name,
            'price_contract': price_contract_name,
        })

        return carry_data_df

    def get_current_and_forward_price_data(self, instrument_code: str) -> pd.DataFrame:
        """
        Возвращает pd.DataFrame с 4 столбцами: PRICE, PRICE_CONTRACT, FORWARD_, FORWARD_CONTRACT.

        Эти данные необходимы, если мы хотим выполнить обратную коррекцию с нуля.

        :param instrument_code: инструмент для получения данных о цене и форварде
        :type instrument_code: str

        :returns: pd.DataFrame
        """

        instrument = Instrument.objects.get(instrument=instrument_code)
        all_price_data = MultiplePriceData.objects.filter(
            instrument=instrument
        ).order_by('datetime')

        # Преобразуем QuerySet Django в DataFrame
        price_data_df = pd.DataFrame.from_records(all_price_data.values())

        # Переименовываем столбцы, если необходимо
        price_data_df = price_data_df.rename(columns={
            'forward': forward_name,
            'price': price_name,
            'forward_contract': forward_contract_name,
            'price_contract': price_contract_name,
        })

        return price_data_df