#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""

import time
from typing import Dict, Union

import numpy as np
import pandas as pd

pd.set_option("display.float_format", lambda x: "%.5f" % x)
pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 1000)

import warnings

warnings.filterwarnings("ignore")


def _treat_parameters(prices, trend="downtrend", window=5, limit=1):
    """Checking all parameters"""
    if not isinstance(limit, int):
        raise ValueError("Limit parameter must be a interger value.")
    if (not isinstance(window, int)) or (window < limit) or (window < 1):
        raise ValueError(
            "Window parameter must be a integer and greater than limit value (in days)."
        )
    if not isinstance(trend, str) or trend.lower() not in ["uptrend", "downtrend"]:
        raise ValueError(
            "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
        )
    if (
        not isinstance(prices, pd.core.frame.DataFrame)
        or prices.empty
        or prices.shape[1] > 1
    ):
        raise ValueError(
            "Input must be a dataframe containing one column and its index must be in datetime format."
        )


def detecttrend(
    df_prices, trend: str = "downtrend", limit: int = 5, window: int = 21, **kwargs
) -> pd.DataFrame:
    """It searches for trends on timeseries.
    Parameters:
        df_price (dataframe): timeseries.
        trend    (string):    the desired trend to be analyzed.
        limit    (int):       optional, the minimum value that represents the number of consecutive days (or another period of time) to be considered a trend.
        window   (int):       optional, the maximum period of time to be considered a trend.
    Returns:
        getTrend2 (dataframe): dataframe containing all trends within given window.
    """
    if not pd.api.types.is_datetime64_ns_dtype(df_prices.index.dtype):
        df_prices.index = pd.to_datetime(df_prices.index, format=kwargs.get("format"))

    _treat_parameters(df_prices, trend, limit, window)

    start = time.time()
    df_prices = df_prices.sort_index()
    i = 0
    df_array = df_prices.reset_index().reset_index().values
    prices, date, index = df_array[:, 2], df_array[:, 1], df_array[:, 0]
    getTrend = np.empty([1, 6], dtype=object)

    while True:
        price2 = prices[i]
        price1 = prices[i + 1]
        if trend.lower() == "downtrend" and price1 < price2:
            go_trend = True
        elif trend.lower() == "uptrend" and price1 > price2:
            go_trend = True
        else:
            go_trend = False

        if go_trend:
            trend_df = np.empty([1, 6], dtype=object)
            try:
                found = df_array[i : (i + window)]
            except:
                found = df_array[i:]  # if len(array)<window size
            if trend.lower() == "downtrend":
                min_interval = found[np.where(found[:, 2] > price2)]
            elif trend.lower() == "uptrend":
                min_interval = found[np.where(found[:, 2] < price2)]

            if list(min_interval):
                min_interval = df_array[found[0][0] : min_interval[0][0]]
                if trend.lower() == "downtrend":
                    priceMax = np.max(min_interval[:, 2])
                elif trend.lower() == "uptrend":
                    priceMax = np.min(min_interval[:, 2])
                location_max = min_interval[np.where(min_interval == priceMax)[0], :][
                    0
                ][0]
                found2 = min_interval[np.where(min_interval[:, 0] > location_max)]
                if found2.size == 0:
                    found2 = min_interval
                if trend.lower() == "downtrend":
                    priceMin = np.min(found2[:, 2])
                elif trend.lower() == "uptrend":
                    priceMin = np.max(found2[:, 2])
                date_max = min_interval[np.where(min_interval[:, -1] == priceMax)][0][1]
                date_min = found2[np.where(found2[:, -1] == priceMin)][-1][1]
                location_min = found2[np.where(found2 == priceMin)[0], :][0][0]
            else:  # the first value is maximum or the minimum (uptrend)
                min_interval = found
                if trend.lower() == "downtrend":
                    priceMin = np.min(min_interval[:, 2])
                elif trend.lower() == "uptrend":
                    priceMin = np.max(min_interval[:, 2])
                location_min = min_interval[np.where(min_interval == priceMin)[0], :][
                    0
                ][0]
                if trend.lower() == "downtrend":
                    priceMax = np.max(min_interval[:, 2])  # min_interval[0][-1]
                elif trend.lower() == "uptrend":
                    priceMax = np.min(min_interval[:, 2])  # min_interval[0][-1]
                location_max = min_interval[np.where(min_interval == priceMax)[0], :][
                    0
                ][0]  # min_interval[0][0]
                date_max = min_interval[np.where(min_interval[:, -1] == priceMax)][-1][
                    1
                ]  # min_interval[0][1]
                date_min = min_interval[np.where(min_interval[:, -1] == priceMin)][-1][
                    1
                ]  # min_interval[-1][1]

            trend_df[0, 0] = date_max  # from
            trend_df[0, 1] = date_min  # to
            trend_df[0, 2] = priceMax  # price0
            trend_df[0, 3] = priceMin  # price1
            trend_df[0, 4] = location_max  # index_from
            trend_df[0, 5] = location_min  # index_to

            if trend_df[0, 5] - trend_df[0, 4] >= limit:
                getTrend = np.vstack([getTrend, trend_df])
                i = location_min - 1

        i += 1
        if i >= prices.shape[0] - 1:
            break

    getTrend2 = pd.DataFrame(getTrend)
    getTrend2.columns = ["from", "to", "price0", "price1", "index_from", "index_to"]

    getTrend2["time_span"] = getTrend2["index_to"] - getTrend2["index_from"]
    getTrend2 = getTrend2[getTrend2["time_span"] > 0]
    getTrend2["time_span"] = pd.to_numeric(getTrend2["time_span"])

    if trend == "downtrend":
        getTrend2["drawdown"] = [
            abs(getTrend2["price0"].iloc[x] - getTrend2["price1"].iloc[x])
            / max(getTrend2["price0"].iloc[x], getTrend2["price1"].iloc[x])
            for x in range(getTrend2.shape[0])
        ]
        getTrend2.columns = [
            "Peak Date",
            "Valley Date",
            "Peak",
            "Valley",
            "index_peak",
            "index_valley",
            "time_span",
            "drawdown",
        ]
    elif trend == "uptrend":
        getTrend2["drawup"] = [
            np.inf
            if min(getTrend2["price0"].iloc[x], getTrend2["price1"].iloc[x]) == 0
            else abs(getTrend2["price0"].iloc[x] - getTrend2["price1"].iloc[x])
            / min(getTrend2["price0"].iloc[x], getTrend2["price1"].iloc[x])
            for x in range(getTrend2.shape[0])
        ]
        getTrend2.columns = [
            "Valley Date",
            "Peak Date",
            "Valley",
            "Peak",
            "index_valley",
            "index_peak",
            "time_span",
            "drawup",
        ]

    print("Trends detected in {} secs".format(round((time.time() - start), 2)))
    return getTrend2.sort_values(getTrend2.columns[0])


def get_trends_labels(
    df: pd.DataFrame,
    labels: Dict[str, Union[int, float, str]] = None,
    window: int = 252,
    limit: int = 5,
) -> pd.DataFrame:
    """
    Adds a 'label' column to the dataframe based on detected trends.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with DatetimeIndex and 'Close' column.
    labels : Dict[str, Union[int, float, str]], optional
        Dictionary defining which trends to calculate and their values.
        Example: {"uptrend": 1, "downtrend": -1, "notrend": 0}
        Default: {"uptrend": 1, "downtrend": -1, "notrend": 0}
    window : int, optional
        Window for trend detection. Default: 252
    limit : int, optional
        Limit for trend detection. Default: 5

    Returns
    -------
    pd.DataFrame
        Dataframe with the new 'label' column added.

    Examples
    --------
    >>> df_labeled = get_trends_labels(df)
    >>> df_only_up = get_trends_labels(df, labels={"uptrend": 1, "notrend": 0})
    >>> df_custom = get_trends_labels(df, labels={"uptrend": "BUY", "downtrend": "SELL"})
    """

    if labels is None:
        labels = {"uptrend": 1, "downtrend": -1, "notrend": 0}

    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    default_label: Union[int, float, str] = labels.get("notrend", 0)
    df["label"] = default_label

    if "uptrend" in labels:
        try:
            uptrends: pd.DataFrame = detecttrend(
                df,
                trend="uptrend",
                window=window,
                limit=limit,
            )

            if not uptrends.empty:
                uptrend_label: Union[int, float, str] = labels["uptrend"]

                for _, row in uptrends.iterrows():
                    start_date: pd.Timestamp = row["Valley Date"]
                    end_date: pd.Timestamp = row["Peak Date"]

                    mask: pd.Series = (df.index >= start_date) & (df.index <= end_date)

                    df.loc[mask, "label"] = uptrend_label

        except Exception as e:
            print(f"Warning: Error processing uptrends: {e}")

    if "downtrend" in labels:
        try:
            downtrends: pd.DataFrame = detecttrend(
                df,
                trend="downtrend",
                window=window,
                limit=limit,
            )

            if not downtrends.empty:
                downtrend_label: Union[int, float, str] = labels["downtrend"]

                for _, row in downtrends.iterrows():
                    start_date: pd.Timestamp = row["Peak Date"]
                    end_date: pd.Timestamp = row["Valley Date"]

                    mask: pd.Series = (df.index >= start_date) & (df.index <= end_date)

                    df.loc[mask, "label"] = downtrend_label

        except Exception as e:
            print(f"Warning: Error processing downtrends: {e}")

    return df
