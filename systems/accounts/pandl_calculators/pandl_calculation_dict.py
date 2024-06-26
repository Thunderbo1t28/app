import datetime
import numpy as np
import pandas as pd
from systems.accounts.pandl_calculators.pandl_generic_costs import (
    pandlCalculationWithGenericCosts,
)


class pandlCalculationWithoutPositions(pandlCalculationWithGenericCosts):
    def __init__(
        self,
        pandl_in_base_currency: pd.Series,
        costs_pandl_in_base_currency: pd.Series,
        capital: pd.Series,
    ):

        super().__init__(price=pd.Series(dtype="float64"), capital=capital)

        if not isinstance(pandl_in_base_currency, pd.Series):
            raise TypeError("pandl_in_base_currency must be a pd.Series")
        if not isinstance(costs_pandl_in_base_currency, pd.Series):
            raise TypeError("costs_pandl_in_base_currency must be a pd.Series")
        #if not pandl_in_base_currency.index.equals(capital.index):
            #raise ValueError("pandl_in_base_currency index must match capital index")
        #if not costs_pandl_in_base_currency.index.equals(capital.index):
            #raise ValueError("costs_pandl_in_base_currency index must match capital index")


        self._pandl_in_base_currency = pandl_in_base_currency
        self._costs_pandl_in_base_currency = costs_pandl_in_base_currency

    ## used for summing account curves
    def pandl_in_base_currency(self) -> pd.Series:
        return self._pandl_in_base_currency

    def costs_pandl_in_base_currency(self) -> pd.Series:
        return self._costs_pandl_in_base_currency

    def net_pandl_in_instrument_currency(self):
        raise NotImplementedError

    def pandl_in_instrument_currency(self):
        raise NotImplementedError

    def costs_pandl_in_instrument_currency(self):
        raise NotImplementedError

    def net_pandl_in_points(self):
        raise NotImplementedError

    def pandl_in_points(self):
        raise NotImplementedError

    def costs_pandl_in_points(self):
        raise NotImplementedError

    @property
    def price(self):
        raise NotImplementedError

    @property
    def positions(self):
        raise NotImplementedError

    @property
    def value_per_point(self):
        raise NotImplementedError

    @property
    def fx(self):
        raise NotImplementedError

    @property
    def _index_to_align_capital_to(self):
        return self.pandl_in_base_currency().index


class dictOfPandlCalculatorsWithGenericCosts(dict):
    def sum(self, capital) -> pandlCalculationWithoutPositions:
        if not isinstance(capital, pd.Series):
            
            DEFAULT_DATES = pd.date_range(
                start=datetime.datetime(2010, 1, 1), freq="B", end=datetime.datetime.now()
            )
            capital = pd.Series(np.full(len(DEFAULT_DATES), capital), index=DEFAULT_DATES)
        #print(capital)
        pandl_in_base_currency = self.sum_of_pandl_in_base_currency()
        costs_pandl_in_base_currency = self.sum_of_costs_pandl_in_base_currency()

        pandl_calculator = pandlCalculationWithoutPositions(
            pandl_in_base_currency=pandl_in_base_currency,
            costs_pandl_in_base_currency=costs_pandl_in_base_currency,
            capital=capital,
        )

        return pandl_calculator

    def sum_of_pandl_in_base_currency(self) -> pd.Series:
        list_of_pandl_in_base_currency = self.list_of_pandl_in_base_currency
        
        if not list_of_pandl_in_base_currency:
            DEFAULT_DATES = pd.date_range(
                start=datetime.datetime(2010, 1, 1), freq="B", end=datetime.datetime.now()
            )
            list_of_pandl_in_base_currency.append(pd.Series(np.full(len(DEFAULT_DATES), 0.0), index=DEFAULT_DATES))
        #if not all(isinstance(x, pd.Series) for x in list_of_pandl_in_base_currency):
            #raise TypeError("All elements in list_of_pandl_in_base_currency must be pd.Series")

        return sum_list_of_pandl_curves(list_of_pandl_in_base_currency)

    def sum_of_costs_pandl_in_base_currency(self) -> pd.Series:
        list_of_costs_pandl_in_base_currency = self.list_of_costs_pandl_in_base_currency
        if not list_of_costs_pandl_in_base_currency:
            DEFAULT_DATES = pd.date_range(
                start=datetime.datetime(2010, 1, 1), freq="B", end=datetime.datetime.now()
            )
            list_of_costs_pandl_in_base_currency.append(pd.Series(np.full(len(DEFAULT_DATES), 0.0), index=DEFAULT_DATES))
        #if not all(isinstance(x, pd.Series) for x in list_of_costs_pandl_in_base_currency):
            #raise TypeError("All elements in list_of_costs_pandl_in_base_currency must be pd.Series")

        return sum_list_of_pandl_curves(list_of_costs_pandl_in_base_currency)

    @property
    def list_of_pandl_in_base_currency(self) -> list:
        return self._list_of_attr("pandl_in_base_currency")

    @property
    def list_of_costs_pandl_in_base_currency(self) -> list:
        return self._list_of_attr("costs_pandl_in_base_currency")

    def _list_of_attr(self, attr_name) -> list:
        #print(attr_name)
        list_of_methods = [
            getattr(pandl_item, attr_name) for pandl_item in self.values()
        ]
        list_of_attr = [x() for x in list_of_methods]

        return list_of_attr


def sum_list_of_pandl_curves(list_of_pandl_curves: list):
    df_of_pandl_curves = pd.concat(list_of_pandl_curves, axis=1, sort=True)
    summed_pandl_curve = df_of_pandl_curves.sum(axis=1)

    return summed_pandl_curve
