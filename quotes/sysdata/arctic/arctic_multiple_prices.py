"""
Read and write data from mongodb for 'multiple prices'

"""
import pandas as pd
from quotes.sysdata.arctic.arctic_connection import arcticData
from quotes.sysdata.futures.multiple_prices import (
    futuresMultiplePricesData,
)
from quotes.sysobjects.multiple_prices import futuresMultiplePrices
from quotes.sysobjects.dict_of_named_futures_per_contract_prices import (
    list_of_price_column_names,
    contract_name_from_column_name,
)
#from syslogging.logger import *

MULTIPLE_COLLECTION = "futures_multiple_prices"


class arcticFuturesMultiplePricesData(futuresMultiplePricesData):
    """
    Class to read / write multiple futures price data to and from arctic
    """

    def __init__(
        self, mongo_db=None, #log=get_logger("arcticFuturesMultiplePricesData")
    ):

        super().__init__()#log=log)

        self._arctic = arcticData(MULTIPLE_COLLECTION, mongo_db=mongo_db)

    def __repr__(self):
        return repr(self._arctic)

    @property
    def arctic(self):
        return self._arctic

    def get_list_of_instruments(self) -> list:
        return self.arctic.get_keynames()

    def _get_multiple_prices_without_checking(
        self, instrument_code: str
    ) -> futuresMultiplePrices:
        data = self.arctic.read(instrument_code)

        return futuresMultiplePrices(data)

    def _delete_multiple_prices_without_any_warning_be_careful(
        self, instrument_code: str
    ):

        self.arctic.delete(instrument_code)
        '''self.log.debug(
            "Deleted multiple prices for %s from %s" % (instrument_code, str(self))
        )'''
        print(f"Deleted multiple prices for {instrument_code} from {str(self)}")

    def _add_multiple_prices_without_checking_for_existing_entry(
        self, instrument_code: str, multiple_price_data_object: futuresMultiplePrices
    ):

        multiple_price_data_aspd = pd.DataFrame(multiple_price_data_object)
        multiple_price_data_aspd = _change_contracts_to_str(multiple_price_data_aspd)

        self.arctic.write(instrument_code, multiple_price_data_aspd)
        '''self.log.debug(
            "Wrote %s lines of prices for %s to %s"
            % (len(multiple_price_data_aspd), instrument_code, str(self)),
            instrument_code=instrument_code,
        )'''
        print(f"Wrote {len(multiple_price_data_aspd)} lines of prices for {instrument_code} to {str(self)}")


def _change_contracts_to_str(multiple_price_data_aspd):
    for price_column in list_of_price_column_names:
        multiple_price_data_aspd[price_column] = multiple_price_data_aspd[
            price_column
        ].astype(float)

        contract_column = contract_name_from_column_name(price_column)
        multiple_price_data_aspd[contract_column] = multiple_price_data_aspd[
            contract_column
        ].astype(str)

    return multiple_price_data_aspd
