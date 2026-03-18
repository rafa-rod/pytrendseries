#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""

import time
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd

plt.style.use("fivethirtyeight")


def plot_trend(
    df: pd.DataFrame,
    getTrend3: pd.DataFrame,
    trend="downtrend",
    year: Union[bool, int] = None,
    **kwargs,
):  # pragma: no cover
    """To plot all trend found.
    Parameters:
        df        (dataframe): timeserie.
        getTrend3 (dataframe): dataframe with all interval of trend found in timeserie.
        trend     (string):    the desired trend to be analyzed.
        year      (int):       optional, when is desire to analyse a specif part of the serie by filterring year.
    Returns:
        simple matplotlib chart
    """
    start = time.time()
    if not pd.api.types.is_datetime64_ns_dtype(df.index.dtype):
        df.index = pd.to_datetime(df.index, format=kwargs.get("format"))

    for col in getTrend3.columns[:1]:
        getTrend3[col] = pd.to_datetime(getTrend3[col])

    if year:
        df = df[pd.DatetimeIndex(df.index).year >= year]
        getTrend3 = getTrend3[getTrend3[getTrend3.columns[0]].dt.year >= year]

    plt.figure(figsize=(14, 5))
    plt.plot(df, alpha=0.6)
    location_x = getTrend3.values[:, 0]
    location_y = getTrend3.values[:, 1]
    if trend == "uptrend":
        color = "green"
    elif trend == "downtrend":
        color = "red"
    for i in range(location_x.shape[0]):
        plt.axvspan(location_x[i], location_y[i], alpha=0.3, color=color)
    plt.grid(axis="x")
    plt.show()
    print("Plotted in {} secs".format(round((time.time() - start), 2)))


def _serie_maxdd(precos):
    "Auxiliary function to plotting timeseries drawdowns"
    df0 = precos.copy()
    df0["peak"] = df0.expanding().max()
    df0["maxdd"] = abs(df0[df0.columns[0]] / df0["peak"] - 1)
    return df0


def plot_drawdowns(
    precos: pd.DataFrame, figsize=(10, 4), color="gray", alpha=0.6, axis="y", **kwargs
):
    """To plot all timeseries drawdowns.
    Parameters:
        df    (dataframe): timeserie.
    Returns:
        the chart
    """
    df0 = _serie_maxdd(precos)
    plt.figure(figsize=figsize)
    plt.fill_between(
        df0["maxdd"].index,
        -df0["maxdd"].values * 100,
        color=kwargs.get("color"),
        alpha=kwargs.get("alpha"),
    )
    plt.title(label=kwargs.get("title"))
    plt.ylabel("%", rotation=0, labelpad=15)
    plt.box(False)
    plt.grid(axis=axis)
    plt.show()


def plot_evolution(
    precos: pd.DataFrame,
    figsize=(10, 4),
    colors=["gray", "red"],
    alphas=[1, 0.6],
    axis="y",
    **kwargs,
):
    """To plot evolution of drawdowns.
    Parameters:
        df    (dataframe): timeserie.
    Returns:
        the chart
    """
    df0 = _serie_maxdd(precos)
    df0.drop("maxdd", axis=1, inplace=True)
    plt.figure(figsize=figsize)
    cols = df0.columns.tolist()
    plt.plot(df0[cols[0]], color=colors[0], alpha=alphas[0])
    plt.plot(df0[cols[1]], color=colors[1], alpha=alphas[1])
    plt.title(label=kwargs.get("title"))
    plt.box(False)
    plt.grid(axis=axis)
    plt.show()
