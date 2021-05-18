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

pd.set_option('display.float_format', lambda x: '%.5f' % x)
pd.set_option('display.max_rows',100)
pd.set_option('display.max_columns',10)
pd.set_option('display.width',1000)

import warnings
warnings.filterwarnings('ignore')

def _remove_overlap_data(getTrend): # pragma: no cover
    ''' Remove overlap data'''
    getTrend3 = getTrend.groupby('index_to', as_index= False).nth([0]) 
    if getTrend3.empty: getTrend3 = getTrend.copy()
    else:
        x=0
        while True:
            from_=getTrend3['from'].tolist()[x+1:]
            to_ = getTrend3['to'].iloc[x]
            retirar=[t for t in from_ if t < to_]
            if retirar:
                getTrend3 = getTrend3[~getTrend3['from'].isin(retirar)]
            x+=1
            if x >= len(getTrend3['to'])-1: break
    return getTrend3

def _treat_parameters(prices, trend="downtrend" ,limit=5, window=1, quantile=None, year=None):
    '''Checking all parameters'''
    if isinstance(limit, int)==False:
            raise ValueError("Limit parameter must be a interger value.")
    if quantile is not None:
        if (isinstance(quantile, float)==False) or (quantile>1) or (quantile<=0):
            raise ValueError("Quantile parameter must be a float value between 0-1.")
    if (isinstance(window, int)==False) or (window<limit) or (window<1):
            raise ValueError("Window parameter must be a integer and greater than limit value (in days).")
    if year is not None:
        if (isinstance(year, int)==False) or (year<1):
            raise ValueError("Year parameter must be a integer value.")
    if isinstance(trend, str)==False or trend.lower() not in ["uptrend", "downtrend"]:
        raise ValueError("Trend parameter must be string. Choose only 'uptrend' or 'downtrend'.")
    if isinstance(prices, pd.core.frame.DataFrame):
        if prices.empty or ('date' not in prices.columns.tolist()) or (pd.api.types.is_datetime64_ns_dtype(prices.date.dtype)==False) and prices.shape[1]!=2:
            raise ValueError("Input must be a dataframe containing two columns, one of them called 'date' in datetime format.")
    if isinstance(prices, pd.core.frame.DataFrame)==False:
        raise ValueError("Input must be a dataframe containing two columns, one of them called 'date' in datetime format.")
    if quantile is not None and limit is not None:
        raise ValueError("Choose just one parameter (quantile or limit).")

def detecttrend(df_prices, trend="downtrend" ,limit=5, window=21, quantile=None, year=None):
    '''It searches for trends on timeseries.
    Parameters:
        df_price (dataframe): timeserie.
        trend    (string):    the desired trend to be analyzed.
        limit    (int):       optional, the minimum value that represents the number of consecutive days (or anohter period of time) to be considered a trend.
        window   (int):       optional, the maximum period of time to be considered a trend.
        quantile (float):     optional, similar to limit parameter that represents the percentage of correspondency of "limit" most found.
        year     (int):       optional, when is desire to analyse a specif part of the serie by filterring year.
    Returns:
        getTrend5 (dataframe): dataframe with all interval of trend found.
        quantile  (dataframe): dataframe showing the percentage/days that represents the whole consective days to be considered a trend.
    '''
    _treat_parameters(df_prices, trend, limit, window, quantile, year)

    start=time.time()
    df_prices = df_prices.sort_values("date")
    if year: index_start = df_prices[df_prices['date'].dt.year>=year].index[0]
    else: index_start = 0 
    df=df_prices.copy()
    df_array = df.reset_index().values
    prices, date, index = df_array[:,2], df_array[:,1], df_array[:,0]
    getTrend = np.empty([1, 6], dtype=object)
    for i in tqdm(range(index_start,prices.shape[0]-window)):
        priceMin = prices[i]
        price1 = prices[i+1]
        if trend.lower()=="uptrend" and price1 > priceMin: go_trend=True
        elif trend.lower()=="downtrend" and price1 < priceMin: go_trend=True
        else: go_trend=False
        
        if go_trend:
            index_from = index[i]
            since = date[i]
            trend_df = np.empty([1, 6], dtype=object)

            found = df_array[i:(i+window+1)]
            if trend.lower()=="uptrend":
                location_min = found[np.where(found[:,2]<priceMin)]
            elif trend.lower()=="downtrend":
                location_min = found[np.where(found[:,2]>priceMin)]
                
            if list(location_min): 
                location_min = location_min[0][0]
                found2 = found[np.where(found[:,0]<location_min)]
                if not list(found2): found2=found[-1].reshape(1,-1)
            else:
                found2=found
                
            if trend.lower()=="uptrend": priceMax = np.max(found2[:,2])
            elif trend.lower()=="downtrend": priceMax = np.min(found2[:,2])
            
            location_max = found2[np.where(found2==priceMax)[0],:][0]
            if location_max[0] == prices.shape[0]: break
            to, index_to = location_max[1], location_max[0]
    
            trend_df[0,0] = since #from
            trend_df[0,1] = to #to
            trend_df[0,2] = priceMin #price0
            trend_df[0,3] = priceMax #price1
            trend_df[0,4] = index_from #index_from
            trend_df[0,5] = index_to #index_to
                
            getTrend = np.vstack([getTrend, trend_df])         
          
    getTrend2 = pd.DataFrame(getTrend)
    getTrend2.columns = ['from','to','price0','price1','index_from','index_to']
    
    getTrend2['time_span'] = getTrend2['index_to'] - getTrend2['index_from']
    getTrend2=getTrend2[getTrend2['time_span']>0]
    getTrend2['time_span'] = pd.to_numeric(getTrend2['time_span'])
    quantileValue = getTrend2['time_span'].describe([0.25,0.5,0.75,0.8,0.85,0.9,0.925,0.95,0.975,0.99])  
    if quantile:
        limit = getTrend2['time_span'].quantile(quantile)

    getTrend4 = getTrend2[getTrend2['time_span']>=limit]
    getTrend4 = getTrend4.sort_values("from")
    
    if trend == "downtrend":
        getTrend4["drawdown"] = [abs(getTrend4["price0"].iloc[x]-getTrend4["price1"].iloc[x])/max(getTrend4["price0"].iloc[x],getTrend4["price1"].iloc[x]) for x in range(getTrend4.shape[0])]
        getTrend5 = _remove_overlap_data(getTrend4)
    elif trend == "uptrend":
        getTrend4["run_up"]  = [abs(getTrend4["price0"].iloc[x]-getTrend4["price1"].iloc[x])/min(getTrend4["price0"].iloc[x],getTrend4["price1"].iloc[x]) for x in range(getTrend4.shape[0])]  
        getTrend5 = _remove_overlap_data(getTrend4)
        
    print("Trends detected in {} secs".format(round((time.time()-start),2)))
    return getTrend5.sort_values("from"), quantileValue.to_frame()