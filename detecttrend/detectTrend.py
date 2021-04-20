#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""
import pandas as pd
from pandas.core.common import flatten
import os, time
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

#import seaborn as sns
#sns.set_style("white")

pd.set_option('display.float_format', lambda x: '%.5f' % x)
pd.set_option('display.max_rows',100)
pd.set_option('display.max_columns',10)
pd.set_option('display.width',1000)

import warnings
warnings.filterwarnings('ignore')

def _remove_overlap_data(getTrend3):
    ''' Remove overlap data'''
    retirar_all=[]
    for x in range(len(getTrend3['to'])-1):
        from_=getTrend3['from'].tolist()[x+1:]
        to_ = getTrend3['to'].iloc[x]
        retirar=[t for t in from_ if t < to_]
        if retirar: retirar_all.append(retirar)
    retirar_all = list(flatten(retirar_all))
    getTrend4 = getTrend3[~getTrend3['from'].isin(retirar_all)]
    return getTrend4


def _treat_parameters(prices, trend="uptrend" ,limit=5, window=1, quantil=None, year=None):
    '''Checking all parameters'''
    if isinstance(limit, int)==False:
            raise Exception("Limit parameter must be a interger value.")
    if quantil is not None:
        if (isinstance(quantil, float)==False) or (quantil>1) or (quantil<=0):
            raise Exception("Quantil parameter must be a float value between 0-1.")
    if (isinstance(window, int)==False) or (window<1):
            raise Exception("Window parameter must be a integer value greater than 1 (in days).")
    if year is not None:
        if (isinstance(year, int)==False) or (year<1):
            raise Exception("Year parameter must be a integer value.")
    if trend.lower() not in ["uptrend", "downtrend"]:
        raise Exception("Choose only 'uptrend' or 'downtrend'.")
    if prices.empty or ('date' not in prices.columns.tolist()) or (pd.api.types.is_datetime64_ns_dtype(prices.date.dtype)==False):
        raise Exception("Dataframe must contain two columns one of them called 'date'. Column date must be in datetime format.")

def maxdradown(prices, getTrend4):
    '''To calculate maxdrawdown in selected window of timeseries'''
    mdd = pd.DataFrame(columns=["maxdrawdown", "peak_date_maxdrawdown", "valley_date_maxdrawdown","peak_price","valley_price"])
    getTrend5 = getTrend4.copy()
    maxdrawdown_lst, peak_date_maxdrawdown_lst, valley_date_maxdrawdown_lst, peak_price_lst, valley_price_lst = [], [], [], [], []
    for x in range(getTrend5.shape[0]):
        from_ = getTrend5["from"].iloc[x]
        to_   = getTrend5["to"].iloc[x]
        interval  = prices[(prices.date>=from_) & (prices.date<=to_)]
        peak  = interval.max().values
        valley = interval.min().values
        maxdrawdown_lst.append( abs(peak[1]-valley[1])/peak[1] )
        peak_date_maxdrawdown_lst.append( peak[0] )
        valley_date_maxdrawdown_lst.append( valley[0] )
        peak_price_lst.append( peak[1] )
        valley_price_lst.append( valley[1] )
    mdd["maxdrawdown"] = maxdrawdown_lst
    mdd["peak_date_maxdrawdown"] = peak_date_maxdrawdown_lst
    mdd["valley_date_maxdrawdown"] = valley_date_maxdrawdown_lst
    mdd["peak_price"] = peak_price_lst
    mdd["valley_price"] = valley_price_lst
    maxmdd = mdd[mdd["maxdrawdown"]==mdd["maxdrawdown"].max()]
    return maxmdd

def detectTrend(df_prices, trend="uptrend" ,limit=5, window=1, quantil=None, year=None, priority="drawdown"):
    ''' Detect trend (up or down) in a timeseries dataframe with columns are date and price.
    It is possible to select window (i.e. 30 days, 126 days, and so on) of analysis or, by default, consider all dates.
    Using quantil (0-1) it is possible to choose trend with a specific percentil.
    Whether using limit value, instead of using quantil, you can manually choose trend in the timeseries.
    Exemple: whether two consecutive prices is rising you might consider this pattern a trend, but if not you can adjust manually using 
    limit parameter greater than 2 or using quantil parameter as 0.95'''
    
    if quantil is not None and limit is not None:
        raise ValueError("Choose just one parameter (quantil or limit).")

    _treat_parameters(df_prices, trend, limit, window, quantil, year)

    start=time.time()
    if year: df = df_prices[df_prices['date'].dt.year>=year]
    else: df=df_prices.copy()
    df_array = df.reset_index().values
    prices, date, indice = df_array[:,2], df_array[:,1], df_array[:,0]
    getTrend, ID = pd.DataFrame(), 0
    for i in tqdm(range(0,prices.shape[0]-window)):
        priceMin = prices[i]
        price1 = prices[i+window]
        if trend.lower()=="uptrend":
            if price1 > priceMin:
                '''up trend'''
                #print(i)
                indice_from = indice[i]
                since = date[i]
                ID+=1
                trend_df = {'ID':ID,'from':since,'to':np.nan,'price0':priceMin,'price1':np.nan,
                         'indice_from':indice_from, 'indice_to':np.nan}
                trend_df = pd.DataFrame.from_dict(trend_df,orient='index').T
                found = df_array[i:(i+window+1)]
                location_min = found[np.where(found[:,2]<priceMin)]
                if list(location_min): 
                    location_min = location_min[0][0]
                    found2 = found[np.where(found[:,0]>location_min)]
                    if not list(found2): found2=found[-1].reshape(1,-1)
                else:
                    found2=found
                priceMax = np.max(found2[:,2])
                location_max = found2[np.where(found2==priceMax)[0],:][0]
                if location_max[0] == prices.shape[0]: break
                if location_max[0] == i: continue
                to, indice_to = location_max[1], location_max[0]
        
                trend_df = {'ID':ID,'from':since,'to':to,'price0':priceMin,'price1':priceMax,
                         'indice_from':indice_from, 'indice_to':indice_to}
                trend_df = pd.DataFrame.from_dict(trend_df,orient='index').T
                getTrend = pd.concat([getTrend, trend_df]).drop_duplicates()
        elif trend.lower()=="downtrend":
            if price1 < priceMin:
                '''down trend'''
                indice_from = indice[i]
                since = date[i]
                ID+=1
                trend_df = {'ID':ID,'from':since,'to':np.nan,'price0':priceMin,'price1':np.nan,
                         'indice_from':indice_from, 'indice_to':np.nan}
                trend_df = pd.DataFrame.from_dict(trend_df,orient='index').T
                found = df_array[i:(i+window+1)]
                location_min = found[np.where(found[:,2]>priceMin)]
                if list(location_min): 
                    location_min = location_min[0][0]
                    found2 = found[np.where(found[:,0]<location_min)]
                    if not list(found2): found2=found[-1].reshape(1,-1)
                else:
                    found2=found
                priceMax = np.min(found2[:,2])
                location_max = found2[np.where(found2==priceMax)[0],:][0]
                if location_max[0] == prices.shape[0]: break
                if location_max[0] == i: continue
                to, indice_to = location_max[1], location_max[0]
        
                trend_df = {'ID':ID,'from':since,'to':to,'price0':priceMin,'price1':priceMax,
                         'indice_from':indice_from, 'indice_to':indice_to}
                trend_df = pd.DataFrame.from_dict(trend_df,orient='index').T
                getTrend = pd.concat([getTrend, trend_df]).drop_duplicates()
            
    getTrend = getTrend.groupby('to', as_index= False).nth([0])       
    getTrend2 = getTrend.copy()
    
    getTrend2['time_on_trend'] = getTrend2['indice_to'] - getTrend2['indice_from']# + 1
    getTrend2=getTrend2[getTrend2['time_on_trend']>0]
    getTrend2['time_on_trend'] = pd.to_numeric(getTrend2['time_on_trend'])
    quantilValue = getTrend2['time_on_trend'].describe([0.25,0.5,0.75,0.8,0.85,0.9,0.925,0.95,0.975,0.99])  
    if quantil:
        limit = getTrend2['time_on_trend'].quantile(quantil)

    getTrend4 = getTrend2[getTrend2['time_on_trend']>=limit]
    
    if trend == "downtrend":
        getTrend4["drawdown"] = [abs(getTrend4["price0"].iloc[x]-getTrend4["price1"].iloc[x])/max(getTrend4["price0"].iloc[x],getTrend4["price1"].iloc[x]) for x in range(getTrend4.shape[0])]
    elif trend == "uptrend":
        getTrend4["buildup"]  = [abs(getTrend4["price0"].iloc[x]-getTrend4["price1"].iloc[x])/min(getTrend4["price0"].iloc[x],getTrend4["price1"].iloc[x]) for x in range(getTrend4.shape[0])]
    
    if priority == "drawdown" and trend == "downtrend":
        getTrend5 = _remove_overlap_data(getTrend4.sort_values("drawdown",ascending=False))
    elif priority == "drawdown" and trend == "uptrend":
        getTrend5 = _remove_overlap_data(getTrend4.sort_values("buildup",ascending=False))
    elif priority == "time_on_trend":
        getTrend5 = _remove_overlap_data(getTrend4.sort_values("time_on_trend",ascending=False))
    elif priority == "first_trend_found":
        getTrend5 = _remove_overlap_data(getTrend4)
        
    print("Concluido em {} segundos".format(round((time.time()-start)/1,2)))
    return getTrend5.sort_values("from"), quantilValue

def plot_trend(df, getTrend3, stock, trend, year):
    df = df[df['date'].dt.year>=year]
    plt.figure(figsize=(14,5))
    plt.plot(df.date,df[stock],alpha=0.6)
    for i in range(len(getTrend3)):
        if trend == "uptrend":
            plt.axvspan(getTrend3['from'].iloc[i], getTrend3['to'].iloc[i],alpha=0.3,color='green')
        elif trend == "downtrend":
            plt.axvspan(getTrend3['from'].iloc[i], getTrend3['to'].iloc[i],alpha=0.3,color='red')         
    #plt.savefig(os.path.join(path_downloads,'trend.png'), dpi=900)
    plt.show()
    
# path_downloads = os.path.join(os.path.expanduser('~'), 'downloads')

# novos_dados = pd.read_csv(os.path.join(path_downloads,"PETR4.csv"))
# novos_dados = novos_dados.sort_values("date")
# novos_dados["date"] = pd.to_datetime(novos_dados["date"])
# precos = novos_dados[['date',"close"]]

# ano = 2005
# trend = "downtrend"
# stock = "close"
# janela = 60
# getTrend3, quantil = detectTrend(precos, trend=trend, priority="first_trend_found",
#                                      window=janela, year=ano)


# plot_trend(precos, getTrend3, stock, trend, ano)

# print("{}".format(maxdradown(precos, getTrend3)))

