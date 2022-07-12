#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

def _treat_parameters(prices):
    '''Checking all parameters'''
    if isinstance(prices, pd.core.frame.DataFrame)==False or prices.empty or prices.shape[1]>1:
        raise ValueError("Input must be a dataframe containing one column and its index must be in datetime format.")

def tuw(df: pd.DataFrame, **kwargs) -> pd.DataFrame:

    if pd.api.types.is_datetime64_ns_dtype(df.index.dtype) == False:
        df.index = pd.to_datetime(df.index, format=kwargs.get('format'))
        
    _treat_parameters(df)

    df0 = df.copy()
    df0["pico"] = df0.expanding().max()
    df1 = df0["pico"].drop_duplicates(keep="first").to_frame().reset_index()
    df1.columns = ['data_inicio',"pico"]
    df1 = df1.set_index("data_inicio")
    df1["pico"] = pd.to_numeric(df1["pico"])
    df1["vale"] = df0.groupby("pico").min().reset_index()[df0.columns[0]].values
    df1["drawdown"]= 1-df1["vale"]/df1["pico"]
    tuw = [df0[(df0.index>=df1.index[x]) & (df0.index<=df1.index[x+1])].shape[0] for x in range(df1.index.shape[0]-1)]
    df1["time underwater"] = tuw + [np.nan]
    df1["data_fim"] = df1.index[1:].tolist() + [np.nan]
    df1 = df1[df1["pico"]!=df1["vale"]]
    return df1.reset_index()