"""
Get data from .csv files used for futures trading

"""

from sysdata.django.django_adjusted_prices import djangoFuturesAdjustedPricesData
from sysdata.django.django_fx_prices import djangoFxPricesData
from sysdata.django.django_instruments import djangoFuturesInstrumentData
from sysdata.django.django_futures_multiple_prices import djangoFuturesMultiplePricesData
from sysdata.django.django_rolls_parameters import djangoRollParametersData
from sysdata.django.django_spread_costs import djangoSpreadCostData
from syscore.constants import arg_not_supplied

from sysdata.data_blob import dataBlob
from sysdata.sim.futures_sim_data_with_data_blob import genericBlobUsingFuturesSimData

from syslogging.logger import *


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
