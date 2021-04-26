#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""
import pandas as pd
import os, time
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

pd.set_option('display.float_format', lambda x: '%.5f' % x)
pd.set_option('display.max_rows',100)
pd.set_option('display.max_columns',10)
pd.set_option('display.width',1000)

import warnings
warnings.filterwarnings('ignore')

def _remove_overlap_data(getTrend):
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
            raise Exception("Limit parameter must be a interger value.")
    if quantile is not None:
        if (isinstance(quantile, float)==False) or (quantile>1) or (quantile<=0):
            raise Exception("quantile parameter must be a float value between 0-1.")
    if (isinstance(window, int)==False) or (window<limit) or (window<1):
            raise Exception("Window parameter must be a integer and greater than limit value (in days).")
    if year is not None:
        if (isinstance(year, int)==False) or (year<1):
            raise Exception("Year parameter must be a integer value.")
    if trend.lower() not in ["uptrend", "downtrend"]:
        raise Exception("Choose only 'uptrend' or 'downtrend'.")
    if prices.empty or ('date' not in prices.columns.tolist()) or (pd.api.types.is_datetime64_ns_dtype(prices.date.dtype)==False):
        raise Exception("Dataframe must contain two columns one of them called 'date'. Column date must be in datetime format.")

def get_peak_valley(price, stock):
    peak   = price[stock].max()
    valley = price[stock].min()
    peak_date = price[price[stock]==peak].date.values[0]
    valley_date = price[price[stock]==valley].date.values[0]
    return peak, valley, peak_date, valley_date
    
def _to_frame_maxdd(array, trend="downtrend"):
    mdd = pd.DataFrame(array)
    mdd.columns = ['peak_price', 'valley_price', 'peak_date', 
                   'valley_date', 'maxdrawdown','time_span']
    mdd = mdd.dropna().drop_duplicates()
    mdd['time_span'] = abs(mdd['valley_date'] - mdd['peak_date'])
    maxmdd = mdd[mdd["maxdrawdown"]==mdd["maxdrawdown"].max()]
    if trend.lower()=="uptrend":
        maxmdd = maxmdd.rename(columns={"maxdrawdown":"maxrunup"})
    return maxmdd

def _get_new_interval(interval, price, stock, trend="downtrend"):
    while interval.size==0:
        price = price[:-1]
        peak, valley, peak_date, valley_date = get_peak_valley(price, stock)
        if trend.lower() == "uptrend":
            interval = price[(price.date <= peak_date) & (price.date >= valley_date)].values
        elif trend.lower() == "downtrend":
            interval = price[(price.date >= peak_date) & (price.date <= valley_date)].values
        if interval.size != 0: break   
    return peak, valley, peak_date, valley_date, interval

def max_trend(price, stock, trend="downtrend", year=None):
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

def detectTrend(df_prices, trend="downtrend" ,limit=5, window=21, quantile=None, year=None):
    ''' Detect trend (up or down) in a timeseries dataframe with columns are date and price.
    It is possible to select window (i.e. 30 days, 126 days, and so on) of analysis or, by default, consider all dates.
    Using quantile (0-1) it is possible to choose trend with a specific percentil.
    Whether using limit value, instead of using quantile, you can manually choose trend in the timeseries.
    Exemple: whether two consecutive prices is rising you might consider this pattern a trend, but if not you can adjust manually using 
    limit parameter greater than 2 or using quantile parameter as 0.95'''
    
    if quantile is not None and limit is not None:
        raise ValueError("Choose just one parameter (quantile or limit).")

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

def plot_trend(df, getTrend3, stock, trend="downtrend", year=None):
    start=time.time()
    if year: df = df[df['date'].dt.year>=year]
    plt.figure(figsize=(14,5))
    plt.plot(df.date,df[stock],alpha=0.6)
    location_x = getTrend3.values[:,0]
    location_y = getTrend3.values[:,1]
    if trend == "uptrend": color = 'green'
    elif trend == "downtrend": color = 'red'
    for i in range(location_x.shape[0]):
        plt.axvspan(location_x[i], location_y[i],alpha=0.3,color=color)
    plt.grid(axis='x')
    plt.show()
    print("Plotted in {} secs".format(round((time.time()-start),2)))
    
def plot_maxdrawdown(df, mdd, stock, trend="downtrend", year=None, style="shadow"):
    if year: df = df[df['date'].dt.year>=year]
    if trend == "uptrend": color = 'green'
    elif trend == "downtrend": color = 'red'
    plt.figure(figsize=(14,5))
    if style=='shadow':
        plt.plot(df.date,df[stock],alpha=0.6)
        plt.axvspan(mdd['valley_date'].values[0], mdd['peak_date'].values[0],alpha=0.3,color=color)
        plt.grid(axis='x')
        plt.show()
    elif style=="area":
        a = mdd['peak_date'].values[0]
        b = mdd['valley_date'].values[0]
        plt.fill_between(df.date, 0, df[stock], where = (df.date >= a),
                         alpha=0.3, facecolor=color)
        plt.fill_between(df.date, 0, df[stock],
                         where = (df.date <= b), 
                         alpha=0.3, facecolor=color)
        plt.plot(df.date,df[stock],alpha=0.6,lw=0.3,color=color)
        plt.scatter(a, mdd["peak_price"].values[0], marker = 'o', color=color)
        plt.scatter(b, mdd["valley_price"].values[0], marker = 'o', color=color)
        plt.grid(axis='x')
        plt.show()  
    elif style=="plotly":
        import plotly.graph_objects as go
        import plotly.io as pio
        pio.renderers.default='browser'

        fig = go.Figure()
        a = mdd['peak_date'].values[0]
        b = mdd['valley_date'].values[0]
        x = df.date
        y = df[stock]
        cut1 = df[(df.date>=a) & (df.date<=b)]
        x_cut1 = cut1.date
        y_cut1 = cut1[stock]
        fig.add_trace(go.Scatter(x=x, y=y,
            fill=None,
            mode='lines',
            line_color=color,
            hovertemplate =
            '<i>Price</i>: R$%{y:.2f}'+
            '<br><b>Date</b>: %{x}<br>'+
            '<b>%{text}</b><extra></extra>',
            text = [stock]*df.shape[0]
            ))
        fig.add_trace(go.Scatter(x=x_cut1, y=y_cut1,
            fill='tonexty',
            mode='lines',
            line_color=color,stackgroup='one',
            hovertemplate =
            '<i>Price</i>: $%{y:.2f}'+
            '<br><b>Date</b>: %{x}<br>'+
            '<b>%{text}</b><extra></extra>',
            text = [stock]*df.shape[0]
            ))
        fig.update_layout(showlegend=False)
        fig.show()