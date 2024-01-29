from copy import copy

import quotes.syscore.pandas.list_of_df
from quotes.syscore.pandas.list_of_df import (
    listOfDataFrames,
    stacked_df_with_added_time_from_list,
)

from backtest.sysquant.estimators.correlations import CorrelationList
from backtest.sysquant.estimators.correlation_over_time import correlation_over_time


def pooled_correlation_estimator(
    data: listOfDataFrames, frequency="W", forward_fill_data=True, **kwargs
) -> CorrelationList:

    copied_data = copy(data)
    if forward_fill_data:
        # NOTE if we're not pooling passes a list of one
        copied_data = copied_data.ffill()

    downsampled_data = copied_data.resample(frequency)

    ## Will need to keep this to adjust lookbacks
    length_adjustment = len(downsampled_data)

    ## We do this to ensure same frequency throughout once concatendate
    data_at_common_frequency = downsampled_data.reindex_to_common_index()

    # Make into one giant dataframe
    pooled_data = quotes.syscore.pandas.list_of_df.stacked_df_with_added_time_from_list(
        data_at_common_frequency
    )

    correlation_list = correlation_over_time(
        pooled_data, **kwargs, length_adjustment=length_adjustment
    )

    return correlation_list
