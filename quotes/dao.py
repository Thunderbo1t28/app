import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F
import pandas as pd
import pytz

from syscore.dateutils import ARBITRARY_START
from quotes.models import AdjustedPrice, FxPriceData, Instrument, MultiplePriceData, RollCalendar, RollParameters, SpreadCosts
from syscore.exceptions import missingData, missingInstrument
from syscore.pandas.frequency import resample_prices_to_business_day_index
from sysdata.django.django_spotfx import djangoFxPricesData
from sysdata.futures.instruments import futuresInstrumentData
from sysobjects.adjusted_prices import futuresAdjustedPrices
from sysobjects.instruments import assetClassesAndInstruments, futuresInstrument, futuresInstrumentWithMetaData, instrumentCosts, instrumentMetaData
from sysobjects.multiple_prices import futuresMultiplePrices
from sysobjects.rolls import rollParameters
from sysobjects.spot_fx_prices import fxPrices

from sysobjects.dict_of_named_futures_per_contract_prices import (
        contract_name_from_column_name,
        price_name,
        carry_name,
        forward_name
    )

class DjangoFuturesSimData(object):
    def __repr__(self):
        return "DjangoFuturesSimData object with %d instruments" % len(
            self.get_instrument_list()
        )
    def __getitem__(self, keyname: str):
        """
         convenience method to get the price, make it look like a dict

        :param keyname: instrument to get prices for
        :type keyname: str

        :returns: pd.DataFrame
        """
        price = self.get_raw_price(keyname)

        return price

    def keys(self) -> list:
        """
        list of instruments in this data set

        :returns: list of str

        >>> data=simData()
        >>> data.keys()
        []
        """
        return self.get_instrument_list()

    def get_instrument_list(self):
        instrument_list = Instrument.objects.values_list('instrument', flat=True).distinct()
        instrument_list_df = pd.DataFrame(instrument_list, columns=['instrument'])
        return list(instrument_list_df['instrument'])
    
    def load_fx_data_from_database(self):
        # Получаем данные из базы данных Django
        fx_price_data = FxPriceData.objects.all()

        # Создаем экземпляр класса fxPricesData
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

    def _get_fx_data_from_start_date(
        self, currency1: str, currency2: str, start_date
    ):
        fx_code = currency1 + currency2
        data = self.load_fx_data_from_database()
        data = data.get_fx_prices(fx_code)
        
        if start_date.tzinfo is None or start_date.tzinfo.utcoffset(start_date) is None:
            # Объект datetime либо не содержит информацию о часовом поясе, либо это "обнуленный" пояс UTC.
            # Преобразуем его в осведомленный о часовом поясе.
            start_date = start_date.replace(tzinfo=pytz.UTC)
        elif start_date.tzinfo is not None:
            # Объект datetime содержит информацию о часовом поясе.
            # Удаляем информацию о часовом поясе.
            start_date = start_date.replace(tzinfo=None)
        # Проверяем, если данные являются DataFrame, преобразуем их в объект Series
        if isinstance(data, pd.DataFrame):
            # Извлекаем столбец с ценами
            data = data.squeeze()

        start_date = start_date.replace(tzinfo=None)
        # Приведение start_date к типу datetime
        #start_date = pd.to_datetime(start_date)
        print(start_date)
        data_after_start = data[start_date:]
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
            adjusted_prices_df.set_index("timestamp", inplace=True)

            adjusted_prices_df = adjusted_prices_df['price']
            # Возвращаем объект futuresAdjustedPrices, используя DataFrame
            return futuresAdjustedPrices(adjusted_prices_df)
        except ObjectDoesNotExist:
            raise ValueError("Instrument {} not found".format(instrument_code))


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
        prices_df.set_index("datetime", inplace=True)

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
        return futuresMultiplePrices(prices_df)

    def get_instrument_meta_data(
        self, instrument_code: str
    ) -> futuresInstrumentWithMetaData:
        """
        Get metadata for a given instrument.

        :param instrument_code: str
        :return: futuresInstrumentWithMetaData
        """
        instrument = Instrument.objects.get(instrument=instrument_code)
        meta_data = instrumentMetaData(
            Description=instrument.description,
            Currency=instrument.currency,
            Pointsize=instrument.point_size,
            AssetClass=instrument.asset_class,
            PerBlock=instrument.per_block,
            Percentage=instrument.percentage,
            PerTrade=instrument.per_trade,
            Region=""  # You might need to adjust this based on your data
        )

        return futuresInstrumentWithMetaData(futuresInstrument(instrument_code), meta_data)

    def get_instrument_object_with_meta_data(
        self, instrument_code: str
    ) -> futuresInstrumentWithMetaData:
        """
        Get metadata for a given instrument.

        :param instrument_code: str
        :return: futuresInstrumentWithMetaData
        """
        instrument = Instrument.objects.get(instrument=instrument_code)
        meta_data = instrumentMetaData(
            Description=instrument.description,
            Currency=instrument.currency,
            Pointsize=instrument.point_size,
            AssetClass=instrument.asset_class,
            PerBlock=instrument.per_block,
            Percentage=instrument.percentage,
            PerTrade=instrument.per_trade,
            Region=""  # You might need to adjust this based on your data
        )

        return futuresInstrumentWithMetaData(futuresInstrument(instrument_code), meta_data)

    def get_spread_cost(self, instrument_code: str) -> float:
        """
        Get spread cost for a given instrument.

        :param instrument_code: str
        :return: float
        """
        instrument = Instrument.objects.get(instrument=instrument_code)
        cost_data = SpreadCosts.objects.get(instrument=instrument)

        return cost_data.spreadcost

    def get_roll_parameters(self, instrument_code: str) -> rollParameters:
        """
        Get roll parameters for a given instrument.

        :param instrument_code: str
        :return: rollParameters
        """
        instrument = Instrument.objects.get(instrument=instrument_code)

        # Retrieve roll parameters data from the database
        roll_params_data = RollParameters.objects.filter(instrument=instrument).first()

        # Extract necessary parameters from the roll_params_data
        hold_rollcycle = roll_params_data.hold_rollcycle
        priced_rollcycle = roll_params_data.priced_rollcycle
        roll_offset_day = roll_params_data.roll_offset_day
        carry_offset = roll_params_data.carry_offset
        approx_expiry_offset = roll_params_data.approx_expiry_offset

        # Create a rollParameters object using the retrieved data
        roll_params = rollParameters(
            hold_rollcycle=hold_rollcycle,
            priced_rollcycle=priced_rollcycle,
            roll_offset_day=roll_offset_day,
            carry_offset=carry_offset,
            approx_expiry_offset=approx_expiry_offset
        )

        return roll_params

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
            'price': price_name,
            'carry': carry_name,
            'price_contract': contract_name_from_column_name(price_name),
            'carry_contract': contract_name_from_column_name(carry_name)
        })
        carry_data_df = carry_data_df[[price_name, carry_name, 
                                       contract_name_from_column_name(price_name), 
                                        contract_name_from_column_name(carry_name)]]
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
            'price': price_name,
            'forward': forward_name,
            'price_contract': contract_name_from_column_name(price_name),
            'forward_contract': contract_name_from_column_name(forward_name)
        })
        price_data_df = price_data_df[[price_name, forward_name, 
                                       contract_name_from_column_name(price_name), 
                                        contract_name_from_column_name(forward_name)]]
        return price_data_df
    
    def get_raw_price_from_start_date(
        self, instrument_code: str, start_date
    ) -> pd.Series:
        """
        For  futures the price is the backadjusted price

        :param instrument_code:
        :return: price
        """
        if start_date.tzinfo is None or start_date.tzinfo.utcoffset(start_date) is None:
            # Объект datetime либо не содержит информацию о часовом поясе, либо это "обнуленный" пояс UTC.
            # Преобразуем его в осведомленный о часовом поясе.
            start_date = start_date.replace(tzinfo=pytz.UTC)
        elif start_date.tzinfo is not None:
            # Объект datetime содержит информацию о часовом поясе.
            # Удаляем информацию о часовом поясе.
            start_date = start_date.replace(tzinfo=None)
        
        # Предполагается, что start_date является объектом типа datetime.datetime
        price = self.get_backadjusted_futures_price(instrument_code)

        return price[start_date:]
    
    def get_rolls_per_year(self, instrument_code: str) -> int:
        roll_parameters = self.get_roll_parameters(instrument_code)
        rolls_per_year = roll_parameters.rolls_per_year_in_hold_cycle()

        return rolls_per_year
    
    def get_raw_cost_data(self, instrument_code: str) -> instrumentCosts:
        """
        Gets cost data for an instrument

        Get cost data

        Execution slippage [half spread] price units
        Commission (local currency) per block
        Commission - percentage of value (0.01 is 1%)
        Commission (local currency) per block

        :param instrument_code: instrument to value for
        :type instrument_code: str

        :returns: dict of floats

        """

        try:
            cost_data_object = self.get_instrument_object_with_meta_data(
                instrument_code
            )
        except missingInstrument:
            self.log.warning(
                "Cost data missing for %s will use zero costs" % instrument_code
            )
            return instrumentCosts()

        spread_cost = self.get_spread_cost(instrument_code)

        instrument_meta_data = cost_data_object.meta_data
        instrument_costs = instrumentCosts.from_meta_data_and_spread_cost(
            instrument_meta_data, spread_cost=spread_cost
        )

        return instrument_costs
    
    def get_value_of_block_price_move(self, instrument_code: str) -> float:
        """
        How much is a $1 move worth in value terms?

        :param instrument_code: instrument to get value for
        :type instrument_code: str

        :returns: float

        """

        instr_object = self.get_instrument_object_with_meta_data(instrument_code)
        meta_data = instr_object.meta_data
        block_move_value = meta_data.Pointsize

        return block_move_value
    
    def get_instrument_currency(self, instrument_code: str) -> str:
        """
        What is the currency that this instrument is priced in?

        :param instrument_code: instrument to get value for
        :type instrument_code: str

        :returns: str

        """
        instr_object = self.get_instrument_object_with_meta_data(instrument_code)
        meta_data = instr_object.meta_data
        currency = meta_data.Currency

        return currency
    
    def get_multiple_prices(self, instrument_code: str) -> futuresMultiplePrices:
        start_date = self.start_date_for_data()

        return self.get_multiple_prices_from_start_date(
            instrument_code, start_date=start_date
        )
    
    def length_of_history_in_days_for_instrument(self, instrument_code: str) -> int:
        return len(self.daily_prices(instrument_code))
    
    def start_date_for_data(self):
        try:
            start_date = getattr(self, "_start_date_for_data_from_config")
        except AttributeError:
            start_date = self._get_and_set_start_date_for_data_from_config()
        return start_date
    def _get_and_set_start_date_for_data_from_config(self) -> datetime:
        start_date = _resolve_start_date(self)
        self._start_date_for_data_from_config = start_date

        return start_date
    
    def daily_prices(self, instrument_code: str) -> pd.Series:
        """
        Gets daily prices

        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.Series

        """
        return self._get_daily_prices_for_directional_instrument(instrument_code)

    def _get_daily_prices_for_directional_instrument(
        self, instrument_code: str
    ) -> pd.Series:
        """
        Gets daily prices

        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.Series

        """
        instrprice = self.get_raw_price(instrument_code)
        if len(instrprice) == 0:
            raise Exception("No adjusted daily prices for %s" % instrument_code)
        dailyprice = resample_prices_to_business_day_index(instrprice)

        return dailyprice
    
    def get_fx_for_instrument(
        self, instrument_code: str, base_currency: str
    ) -> fxPrices:
        """
        Get the FX rate between the FX rate for the instrument and the base (account) currency

        :param instrument_code: instrument to value for
        :type instrument_code: str

        :param base_currency: instrument to value for
        :type instrument_code: str

        :returns: Tx1 pd.Series

        >>> data=simData()
        >>> data.get_fx_for_instrument("wibble", "USD").tail(5)
        2040-12-04    1.0
        2040-12-05    1.0
        2040-12-06    1.0
        2040-12-07    1.0
        2040-12-10    1.0
        Freq: B, dtype: float64
        """

        instrument_currency = self.get_instrument_currency(instrument_code)
        fx_rate_series = self._get_fx_data(instrument_currency, base_currency)

        return fx_rate_series
    
    def get_raw_price(self, instrument_code: str) -> pd.Series:
        """
        Default method to get instrument price at 'natural' frequency

        Will usually be overriden when inherited with specific data source

        :param instrument_code: instrument to get prices for
        :type instrument_code: str

        :returns: pd.Series

        """
        start_date = self.start_date_for_data()

        return self.get_raw_price_from_start_date(
            instrument_code, start_date=start_date
        )
    
    def _get_fx_data(self, currency1: str, currency2: str) -> fxPrices:
        """
        Get the FX rate currency1/currency2 between two currencies
        Or return None if not available

        (Normally we'd over ride this with a specific source)


        """
        start_date = self.start_date_for_data()

        return self._get_fx_data_from_start_date(
            currency1, currency2, start_date=start_date
        )



def _resolve_start_date(sim_data: DjangoFuturesSimData):

    try:
        config = _resolve_config(sim_data)
    except missingData:
        start_date = ARBITRARY_START
    else:
        start_date = getattr(config, "start_date", ARBITRARY_START)

    if isinstance(start_date, datetime.date):
        # yaml parses unquoted date like 2000-01-01 to datetime.date
        start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
    elif not isinstance(start_date, datetime.datetime):
        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        except:
            raise Exception(
                "Parameter start_date %s in config file does not conform to pattern 2020-03-19"
                % str(start_date)
            )

    return start_date

def _resolve_config(sim_data: DjangoFuturesSimData):
    try:
        config = sim_data.parent.config
        return config
    except AttributeError:
        raise missingData