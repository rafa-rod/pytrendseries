#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""
import time
import numpy as np
import pandas as pd

def get_peak_valley(price, stock): # pragma: no cover
    '''Capture peak value  (max value of the serie), valley value (minimum value of the serie)
    Parameters:
        price (dataframe): serie
        stock (string):    column name of dataframe
    Returns:
        peak (float/int):       max value of the serie
        valley (float/int):     min value of the serie
        peak_date (datetime):   date in which max value of the serie occurs
        valley_date (datetime): date in which min value of the serie occurs
    '''
    peak   = price[stock].max()
    valley = price[stock].min()
    peak_date = price[price[stock]==peak].date.values[0]
    valley_date = price[price[stock]==valley].date.values[0]
    return peak, valley, peak_date, valley_date
    
def _to_frame_maxdd(array, trend="downtrend"): # pragma: no cover
    '''Convert resultant array of maxdrawdown into pandas.dataframe'''
    mdd = pd.DataFrame(array)
    mdd.columns = ['peak_price', 'valley_price', 'peak_date', 
                   'valley_date', 'maxdrawdown','time_span']
    mdd = mdd.dropna().drop_duplicates()
    mdd['time_span'] = abs(mdd['valley_date'] - mdd['peak_date'])
    maxmdd = mdd[mdd["maxdrawdown"]==mdd["maxdrawdown"].max()]
    if trend.lower()=="uptrend":
        maxmdd = maxmdd.rename(columns={"maxdrawdown":"maxrunup"})
    return maxmdd

def _get_new_interval(interval, price, stock, trend="downtrend"): # pragma: no cover
    '''Whether the end of the serie the price at this point does not satisfy condition:
       price<=peak and price>=valley. So has no warranty to be the interval that contains maxdrawdown.
       This function search for new interval to satisfy condition.
    '''
    while interval.size==0:
        price = price[:-1]
        peak, valley, peak_date, valley_date = get_peak_valley(price, stock)
        if trend.lower() == "uptrend":
            interval = price[(price.date <= peak_date) & (price.date >= valley_date)].values
        elif trend.lower() == "downtrend":
            interval = price[(price.date >= peak_date) & (price.date <= valley_date)].values
        if interval.size != 0: break   
    return peak, valley, peak_date, valley_date, interval


def getmaxtrend(price, stock, trend="downtrend", year=None):
    '''Given the serie, this function search of maxdrawdown or maxrun up.
    Parameters:
        price (dataframe): serie
        stock (string):    column name of dataframe
        trend (string):    the desired trend to be analyzed
        year  (int):       optional, when is desire to analyse a specif part of the serie by filterring year.
    Returns:
        mxtrend_df (dataframe): dataframe with all data of the points found.
    '''
    start=time.time()
    if year: price = price[price['date'].dt.year>=year]
        
    peak, valley, peak_date, valley_date = get_peak_valley(price, stock)
    
    if trend.lower() == "uptrend":
        interval = price[(price.date >= valley_date) & (price.date <= peak_date)].values
        if interval.size==0:
            peak, valley, peak_date, valley_date, interval = _get_new_interval(interval, price, stock, trend)
        mxtrend = abs(peak-valley)/abs(valley)
    elif trend.lower() == "downtrend":
        interval = price[(price.date >= peak_date) & (price.date <= valley_date)].values
        if interval.size==0:
            peak, valley, peak_date, valley_date, interval = _get_new_interval(interval, price, stock, trend)  
        mxtrend = abs(peak-valley)/abs(peak)
        
    maxtrend_array = np.empty([1, 6], dtype=object)
    maxtrend_array[0,0] =  peak
    maxtrend_array[0,1] =  valley
    maxtrend_array[0,2] =  peak_date
    maxtrend_array[0,3] =  valley_date
    maxtrend_array[0,4] =  mxtrend
    maxtrend_array[0,5] =  abs(peak_date-valley_date)
    
    mxtrend_df = _to_frame_maxdd(maxtrend_array, trend)
    print("MaxDrawDown/Run Up finished in {} secs".format(round((time.time()-start),2)))
    return mxtrend_df