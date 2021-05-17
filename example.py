#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import randrange
import pandas as pd
import numpy as np

from pytrendseries import detecttrend
from pytrendseries import maxtrend
from pytrendseries import vizplot

'''Testing examples with integer random data'''

def random_integer_and_continuously_increasing_data(janela, trend, limit): # pragma: no cove
	random_series = [i+randrange(10) for i in range(1,101)]
	random_series = pd.DataFrame(random_series)
	random_series["date"] = sorted(pd.to_datetime(np.random.randint(1, 101, size=100), unit='d').tolist())
	random_series.columns = ["random","date"]
	random_series = random_series[["date","random"]]
	random_series["random"].plot()

	getTrend3, quantile = detecttrend.detecttrend(random_series, trend=trend, limit=limit,
	                                      window=janela)

	vizplot.plot_trend(random_series, getTrend3, "random", trend)

	maxtrend = maxtrend.getmaxtrend(random_series, "random", trend)
	vizplot.plot_maxdrawdown(random_series, maxtrend, "random", trend, style="shadow")
	return getTrend3, quantile, maxtrend

janela, trend, limit = 3, "downtrend", 2
random_integer_and_continuously_increasing_data(janela, trend, limit)
janela, trend, limit = 3, "uptrend", 2
random_integer_and_continuously_increasing_data(janela, trend, limit)	

def random_integer_and_continuously_decreasing_data(janela, trend, limit): # pragma: no cove
	random_series = [i+randrange(10) for i in reversed(range(1,101))]
	random_series = pd.DataFrame(random_series)
	random_series["date"] = sorted(pd.to_datetime(np.random.randint(1, 101, size=100), unit='d').tolist())
	random_series.columns = ["random","date"]
	random_series = random_series[["date","random"]]
	random_series["random"].plot()

	getTrend3, quantile = detecttrend.detecttrend(random_series, trend=trend, limit=limit,
	                                      window=janela)

	vizplot.plot_trend(random_series, getTrend3, "random", trend)

	maxtrend = maxtrend.getmaxtrend(random_series, "random", trend)
	vizplot.plot_maxdrawdown(random_series, maxtrend, "random", trend, style="shadow")
	return getTrend3, quantile, maxtrend

'''Testing downtrend with integer values in a serie with no uptrend'''
janela, trend, limit = 3, "downtrend", 2
random_integer_and_continuously_decreasing_data(janela, trend, limit)
'''Testing uptrend with integer values in a serie with no uptrend'''
janela, trend, limit = 3, "uptrend", 2
random_integer_and_continuously_decreasing_data(janela, trend, limit)

'''Testing examples with float random data'''

def sine_random_values_testing(janela, trend, limit): # pragma: no cove
	x = np.linspace(1, 101)
	def f(x):
	    return np.sin(x) + np.random.normal(scale=0.1, size=len(x))

	random_series = pd.DataFrame(f(x))
	random_series["date"] = sorted(pd.to_datetime(np.random.randint(1, 101, size=50), unit='d').tolist())
	random_series.columns = ["random","date"]
	random_series = random_series[["date","random"]]
	random_series["random"].plot()


	getTrend3, quantile = detecttrend.detecttrend(random_series, trend=trend, limit=limit,
	                                      window=janela)

	vizplot.plot_trend(random_series, getTrend3, "random", trend)

	maxtrend = maxtrend.getmaxtrend(random_series, "random", trend)
	vizplot.plot_maxdrawdown(random_series, maxtrend, "random", trend, style="shadow")

	return getTrend3, quantile, maxtrend

'''Testing downtrend with float values in a series without long period trend'''
janela, trend, limit = 2, "downtrend", 2
sine_random_values_testing(janela, trend, limit)
'''Testing downtrend with float values in a series without trend'''
janela, trend, limit = 20, "downtrend", 12
sine_random_values_testing(janela, trend, limit)