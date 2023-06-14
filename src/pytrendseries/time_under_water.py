#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""
import pandas as pd
import numpy as np

import warnings

warnings.filterwarnings("ignore")


def _treat_parameters(prices):
    """Checking all parameters"""
    if (
        isinstance(prices, pd.core.frame.DataFrame) == False
        or prices.empty
        or prices.shape[1] > 1
    ):
        raise ValueError(
            "Input must be a dataframe containing one column and its index must be in datetime format."
        )


def tuw(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """The maximum distance in time, from a previous peak to a new peak. it calculates how long it takes an investor to recover its money at the start of the maximum drawdown period.
    Parameters:
        df (dataframe): timeseries.
    Returns:
        df1 (dataframe): dataframe containing inital date (where peak occurs), final date, peak and valley values, drawdown and time underwater.
    """

    if pd.api.types.is_datetime64_ns_dtype(df.index.dtype) == False:
        df.index = pd.to_datetime(df.index, format=kwargs.get("format"))

    _treat_parameters(df)

    df0 = df.copy()
    df0["peak"] = df0.expanding().max()
    df1 = df0["peak"].drop_duplicates(keep="first").to_frame().reset_index()
    df1.columns = ["initial_date", "peak"]
    df1 = df1.set_index("initial_date")
    df1["peak"] = pd.to_numeric(df1["peak"])
    df1["valley"] = df0.groupby("peak").min().reset_index()[df0.columns[0]].values
    df1["drawdown"] = 1 - df1["valley"] / df1["peak"]
    tuw = [
        df0[(df0.index >= df1.index[x]) & (df0.index <= df1.index[x + 1])].shape[0]
        for x in range(df1.index.shape[0] - 1)
    ]
    df1["time underwater"] = tuw + [np.nan]
    df1["final_date"] = df1.index[1:].tolist() + [np.nan]
    df1 = df1[df1["peak"] != df1["valley"]]
    return df1.reset_index()
