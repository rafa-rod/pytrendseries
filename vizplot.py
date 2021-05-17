#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""
import time
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default='browser'

def plot_trend(df, getTrend3, stock, trend="downtrend", year=None): # pragma: no cover
    '''To plot all trend found.
    Parameters:
        df        (dataframe): timeserie.
        getTrend3 (dataframe): dataframe with all interval of trend found in timeserie.
        trend     (string):    the desired trend to be analyzed.
        year      (int):       optional, when is desire to analyse a specif part of the serie by filterring year.
    Returns:
        simple matplotlib chart
    '''
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
    
def plot_maxdrawdown(df, mdd, stock, trend="downtrend", year=None, style="shadow"): # pragma: no cover
    '''To plot all maximum trend found.
    Parameters:
        df    (dataframe): timeserie.
        mdd   (dataframe): dataframe with interval of maximum trend found.
        trend (string):    the desired trend to be analyzed.
        year  (int):       optional, when is desire to analyse a specif part of the serie by filterring year.
        style (string):    optional, you might change style of the chart.
    Returns:
        the chart in a desired style
    '''
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