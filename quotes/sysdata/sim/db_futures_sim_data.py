"""
Get data from mongo and arctic used for futures trading

"""

from quotes.syscore.constants import arg_not_supplied

from quotes.sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from quotes.sysdata.arctic.arctic_multiple_prices import arcticFuturesMultiplePricesData
from quotes.sysdata.arctic.arctic_spotfx_prices import arcticFxPricesData
from quotes.sysdata.csv.csv_instrument_data import csvFuturesInstrumentData
from quotes.sysdata.csv.csv_roll_parameters import csvRollParametersData
from quotes.sysdata.mongodb.mongo_spread_costs import mongoSpreadCostData
from quotes.sysdata.data_blob import dataBlob
from quotes.sysdata.sim.futures_sim_data_with_data_blob import genericBlobUsingFuturesSimData

#from syslogging.logger import *


class dbFuturesSimData(genericBlobUsingFuturesSimData):
    def __init__(
        self, data: dataBlob = arg_not_supplied, #log=get_logger("dbFuturesSimData")
    ):

        if data is arg_not_supplied:
            data = dataBlob(
                #log=log,
                class_list=[
                    arcticFuturesAdjustedPricesData,
                    arcticFuturesMultiplePricesData,
                    arcticFxPricesData,
                    csvFuturesInstrumentData,
                    csvRollParametersData,
                    mongoSpreadCostData,
                ],
            )

        super().__init__(data=data)

    def __repr__(self):
        return "dbFuturesSimData object with %d instruments" % len(
            self.get_instrument_list()
        )


if __name__ == "__main__":
    import doctest

    doctest.testmod()
