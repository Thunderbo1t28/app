import pandas as pd
from datetime import datetime
from sysdata.csv.csv_multiple_prices import csvFuturesMultiplePricesData
from sysdata.csv.csv_adjusted_prices import csvFuturesAdjustedPricesData
from sysdata.csv.csv_spot_fx import csvFxPricesData
from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysdata.data_blob import dataBlob
from sysobjects.spot_fx_prices import fxPrices
from sysobjects.adjusted_prices import futuresAdjustedPrices
from sysobjects.multiple_prices import futuresMultiplePrices
from sysdata.sim.futures_sim_data_with_data_blob import genericBlobUsingFuturesSimData
from syslogging.logger import *
from syscore.dateutils import ARBITRARY_START


class CsvFuturesSimTestData(genericBlobUsingFuturesSimData):
    """
    Specialisation of futuresSimData that allows start and end dates to be configured.
    Useful for unit tests, so that new data added to the CSV price files doesn't mess with assertions,
    or if a test is needed at a certain date/time or period
    """

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    DEFAULT_END_DATE = datetime.strptime("2021-03-08 20:00:00", DATE_FORMAT)

    def __init__(self, start_date=None, end_date=None, log=get_logger("csvFuturesSimTestData")):

        data = dataBlob(
            log=log,
            csv_data_paths=dict(
                csvFuturesAdjustedPricesData="data.test.adjusted_prices_csv",
                csvFuturesInstrumentData="data.test.csvconfig",
            ),
            class_list=[
                csvFuturesAdjustedPricesData,
                csvFuturesMultiplePricesData,
                csvFuturesInstrumentData,
                csvFxPricesData,
                csvRollParametersData,
            ],
        )

        super().__init__(data=data)

        if start_date is not None:
            self._start_date = start_date
        else:
            self._start_date = ARBITRARY_START

        if end_date is not None:
            self._end_date = end_date
        else:
            self._end_date = self.DEFAULT_END_DATE

    def __repr__(self):
        return (
            f"csvFuturesSimTestData with {self.get_instrument_list()} instruments, "
            f"start date {self.start_date.strftime(self.DATE_FORMAT)}, "
            f"end date {self.end_date.strftime(self.DATE_FORMAT)}"
        )

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    # Ваши методы работы с моделями Django и базой данных могут быть добавлены здесь

    def get_backadjusted_futures_price(self, instrument_code: str) -> futuresAdjustedPrices:
        data = AdjustedPrice.objects.filter(instrument_code=instrument_code, date__range=(self.start_date, self.end_date))
        return futuresAdjustedPrices(data)

    def get_multiple_prices(self, instrument_code: str) -> futuresMultiplePrices:
        data = MultiplePrices.objects.filter(instrument_code=instrument_code, date__range=(self.start_date, self.end_date))
        return futuresMultiplePrices(data)

    def get_fx_for_instrument(self, instrument_code: str, base_currency: str) -> fxPrices:
        data = FxPrices.objects.filter(instrument_code=instrument_code, base_currency=base_currency, date__range=(self.start_date, self.end_date))
        return fxPrices(data)

    def daily_prices(self, instrument_code: str) -> pd.Series:
        data = MultiplePrices.objects.filter(instrument_code=instrument_code, date__range=(self.start_date, self.end_date))
        df = read_frame(data, fieldnames=['date', 'price'], index_col='date')
        return df['price']

    def get_instrument_raw_carry_data(self, instrument_code: str) -> pd.DataFrame:
        data = InstrumentRawCarryData.objects.filter(instrument_code=instrument_code, date__range=(self.start_date, self.end_date))
        df = read_frame(data)
        return df

    def get_current_and_forward_price_data(self, instrument_code: str) -> pd.DataFrame:
        data = CurrentAndForwardPriceData.objects.filter(instrument_code=instrument_code, date__range=(self.start_date, self.end_date))
        df = read_frame(data)
        return df

