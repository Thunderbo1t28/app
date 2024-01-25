from django.core.management.base import BaseCommand
import numpy as np
from quotes.dao import DjangoFuturesSimData
import pandas as pd

class Command(BaseCommand):
    help = 'Test EWMA Trading Rule using DjangoFuturesSimData'

    def handle(self, *args, **options):
        sim_data = DjangoFuturesSimData()
        # Например:
        instrument_code='Si'
        start_date=''
        price=sim_data.get_backadjusted_futures_price(instrument_code)
        price = price.set_index('timestamp')
        ewmac=calc_ewmac_forecast(price.price, 32, 128)
        #ewmac.tail(5)
        print(ewmac)
        #multiple_prices = sim_data.get_multiple_prices_from_start_date(instrument_code, start_date)
        #spread_cost = sim_data.get_spread_cost(instrument_code)
        #backadjusted_prices = sim_data.get_backadjusted_futures_price(instrument_code)
        #instrument_meta_data = sim_data.get_instrument_meta_data(instrument_code)
        #roll_parameters = sim_data.get_roll_parameters(instrument_code)
        #instrument_with_meta_data = sim_data.get_instrument_object_with_meta_data(instrument_code)
        #raw_carry_data = sim_data.get_instrument_raw_carry_data(instrument_code)
        #current_forward_price_data = sim_data.get_current_and_forward_price_data(instrument_code)
        
        # Выведите результаты в консоль или сделайте что-то еще
        self.stdout.write(self.style.SUCCESS('Successfully tested EWMA Trading Rule.'))

def calc_ewmac_forecast(price, Lfast, Lslow=None):
    
    price = price.resample("1B").last()
    if Lslow is None:
        Lslow = 4 * Lfast

    fast_ewma = price.ewm(span=Lfast).mean()
    slow_ewma = price.ewm(span=Lslow).mean()
    raw_ewmac = fast_ewma - slow_ewma

    vol = robust_vol_calc(price.diff())

    return raw_ewmac / vol

def robust_vol_calc(
    daily_returns: pd.Series,
    days: int = 35,
    min_periods: int = 10,
    vol_abs_min: float = 0.0000000001,
    vol_floor: bool = True,
    floor_min_quant: float = 0.05,
    floor_min_periods: int = 100,
    floor_days: int = 500,
    backfill: bool = False,
    **ignored_kwargs,
) -> pd.Series:
    """
    Robust exponential volatility calculation, assuming daily series of prices
    We apply an absolute minimum level of vol (absmin);
    and a volfloor based on lowest vol over recent history

    :param x: data
    :type x: Tx1 pd.Series

    :param days: Number of days in lookback (*default* 35)
    :type days: int

    :param min_periods: The minimum number of observations (*default* 10)
    :type min_periods: int

    :param vol_abs_min: The size of absolute minimum (*default* =0.0000000001)
      0.0= not used
    :type absmin: float or None

    :param vol_floor Apply a floor to volatility (*default* True)
    :type vol_floor: bool

    :param floor_min_quant: The quantile to use for volatility floor (eg 0.05
      means we use 5% vol) (*default 0.05)
    :type floor_min_quant: float

    :param floor_days: The lookback for calculating volatility floor, in days
      (*default* 500)
    :type floor_days: int

    :param floor_min_periods: Minimum observations for floor - until reached
      floor is zero (*default* 100)
    :type floor_min_periods: int

    :returns: pd.DataFrame -- volatility measure
    """

    # Standard deviation will be nan for first 10 non nan values
    vol = simple_ewvol_calc(daily_returns, days=days, min_periods=min_periods)
    vol = apply_min_vol(vol, vol_abs_min=vol_abs_min)

    if vol_floor:
        vol = apply_vol_floor(
            vol,
            floor_min_quant=floor_min_quant,
            floor_min_periods=floor_min_periods,
            floor_days=floor_days,
        )

    if backfill:
        # use the first vol in the past, sort of cheating
        vol = backfill_vol(vol)

    return vol

def simple_ewvol_calc(
    daily_returns: pd.Series, days: int = 35, min_periods: int = 10, **ignored_kwargs
) -> pd.Series:

    # Standard deviation will be nan for first 10 non nan values
    vol = daily_returns.ewm(adjust=True, span=days, min_periods=min_periods).std()

    return vol

def apply_min_vol(vol: pd.Series, vol_abs_min: float = 0.0000000001) -> pd.Series:
    vol[vol < vol_abs_min] = vol_abs_min

    return vol

def apply_vol_floor(
    vol: pd.Series,
    floor_min_quant: float = 0.05,
    floor_min_periods: int = 100,
    floor_days: int = 500,
) -> pd.Series:
    # Find the rolling 5% quantile point to set as a minimum
    vol_min = vol.rolling(min_periods=floor_min_periods, window=floor_days).quantile(
        quantile=floor_min_quant
    )

    # set this to zero for the first value then propagate forward, ensures
    # we always have a value
    vol_min.iloc[0] = 0.0
    vol_min.ffill(inplace=True)

    # apply the vol floor
    vol_floored = np.maximum(vol, vol_min)

    return vol_floored


def backfill_vol(vol: pd.Series) -> pd.Series:
    # have to fill forwards first, as it's only the start we want to
    # backfill, eg before any value available

    vol_forward_fill = vol.fillna(method="ffill")
    vol_backfilled = vol_forward_fill.fillna(method="bfill")

    return vol_backfilled