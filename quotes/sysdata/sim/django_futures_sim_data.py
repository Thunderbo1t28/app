"""
Get data from .csv files used for futures trading

"""

from quotes.sysdata.django.django_adjusted_prices import djangoFuturesAdjustedPricesData
from quotes.sysdata.django.django_fx_prices import djangoFxPricesData
from quotes.sysdata.django.django_instruments import djangoFuturesInstrumentData
from quotes.sysdata.django.django_futures_multiple_prices import djangoFuturesMultiplePricesData
from quotes.sysdata.django.django_rolls_parameters import djangoRollParametersData
from quotes.sysdata.django.django_spread_costs import djangoSpreadCostData
from quotes.syscore.constants import arg_not_supplied

from quotes.sysdata.data_blob import dataBlob
from quotes.sysdata.sim.futures_sim_data_with_data_blob import genericBlobUsingFuturesSimData

#from syslogging.logger import *


class djangoFuturesSimData(genericBlobUsingFuturesSimData):
    """
    Uses default paths for .csv files, pass in dict of csv_data_paths to modify
    """

    def __init__(
        self,
    ):

        data = dataBlob(
            #log=log,
            #csv_data_paths=csv_data_paths,
            class_list=[
                djangoFuturesAdjustedPricesData,
                djangoFuturesMultiplePricesData,
                djangoFuturesInstrumentData,
                djangoFxPricesData,
                djangoRollParametersData,
                djangoSpreadCostData,
            ],
        )

        super().__init__(data=data)

    def __repr__(self):
        return "csvFuturesSimData object with %d instruments" % len(
            self.get_instrument_list()
        )
