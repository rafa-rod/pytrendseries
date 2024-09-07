#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""
import pandas as pd
import time
import numpy as np
from tqdm import tqdm
from typing import Union, Tuple

pd.set_option("display.float_format", lambda x: "%.5f" % x)
pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 1000)

import warnings

warnings.filterwarnings("ignore")


def _treat_parameters(prices, trend="downtrend", limit=5, window=1):
    """Checking all parameters"""
    if isinstance(limit, int) == False:
        raise ValueError("Limit parameter must be a interger value.")
    if (isinstance(window, int) == False) or (window < limit) or (window < 1):
        raise ValueError(
            "Window parameter must be a integer and greater than limit value (in days)."
        )
    if isinstance(trend, str) == False or trend.lower() not in ["uptrend", "downtrend"]:
        raise ValueError(
            "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
        )
    if (
        isinstance(prices, pd.core.frame.DataFrame) == False
        or prices.empty
        or prices.shape[1] > 1
    ):
        raise ValueError(
            "Input must be a dataframe containing one column and its index must be in datetime format."
        )


def _calcula_MDD(precos):
    dd_atual = 0
    dd_maximo = 0
    maximo_cota = 0
    maxdd = pd.DataFrame(
        np.array([[np.nan, np.nan, np.nan, np.nan, 0]]),
        columns=["Date Peak", "Date Valley", "Peak", "Valley", "MaxDD"],
    )
    for i in range(len(precos)):
        cota = precos.iloc[i].to_numpy()[0]
        if cota >= maximo_cota:
            maximo_cota = cota
        else:
            dd_atual = (cota / maximo_cota) - 1
        if dd_atual < dd_maximo:
            dd_maximo = -dd_atual
            location_max = precos[precos == maximo_cota].dropna().index[0]
            location_min = precos[precos == cota].dropna().index[0]
            df = pd.DataFrame(
                np.array([[location_max, location_min, maximo_cota, cota, dd_maximo]]),
                columns=["Date Peak", "Date Valley", "Peak", "Valley", "MaxDD"],
            )
            maxdd = pd.concat([maxdd, df])
    for col in maxdd.columns[2:]:
        maxdd[col] = pd.to_numeric(maxdd[col])
    return maxdd[maxdd.MaxDD == maxdd.MaxDD.max()].dropna()


def maxdrawdown(df_prices, window=None, **kwargs) -> pd.DataFrame:
    """It searches for maximum drawdown on timeseries.
    Parameters:
        df_price (dataframe): timeseries.
        window   (int):       optional, the maximum period of time to be considered a trend.
    Returns:
        getTrend5 (dataframe): dataframe containing all maximum drawdowns within given window.
    """
    if pd.api.types.is_datetime64_ns_dtype(df_prices.index.dtype) == False:
        df_prices.index = pd.to_datetime(df_prices.index, format=kwargs.get("format"))

    if window:
        _treat_parameters(df_prices, trend="downtrend", limit=1, window=window)
    else:
        _treat_parameters(df_prices, trend="downtrend", limit=1, window=1)

    start = time.time()
    final = pd.DataFrame()
    if window:
        for i in tqdm(range(0, df_prices.shape[0] + window, window)):
            try:
                dd = _calcula_MDD(df_prices[i : i + window])
            except:
                dd = _calcula_MDD(df_prices[i:])
            if dd.empty:
                continue
            final = pd.concat([final, dd])
    else:
        dd = _calcula_MDD(df_prices)
        final = pd.concat([final, dd])

    print("Trends detected in {} secs".format(round((time.time() - start), 2)))
    return final.sort_values("MaxDD", ascending=False)


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
        getTrend5 (dataframe): dataframe containing all trends within given window.
    """
    if pd.api.types.is_datetime64_ns_dtype(df_prices.index.dtype) == False:
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
                ][
                    0
                ]  # min_interval[0][0]
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
    elif trend == "uptrend":
        getTrend2["drawup"] = [
            np.inf
            if min(getTrend2["price0"].iloc[x], getTrend2["price1"].iloc[x])==0
            else abs(getTrend2["price0"].iloc[x] - getTrend2["price1"].iloc[x])
            / min(getTrend2["price0"].iloc[x], getTrend2["price1"].iloc[x])
            for x in range(getTrend2.shape[0])
        ]

    print("Trends detected in {} secs".format(round((time.time() - start), 2)))
    return getTrend2.sort_values("from")
