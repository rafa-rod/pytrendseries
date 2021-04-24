<p align="center">
  <img width=60% src="https://github.com/rafa-rod/detectTrend/blob/main/media/maxdd_area.png">
</p>

<!-- buttons -->
<p align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-v3-brightgreen.svg"
            alt="python"></a> &nbsp;
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg"
            alt="MIT license"></a> &nbsp;
</p>

<!-- content -->

**DetectTrend** is a Python library for detection of trends in time series like: stock prices, monthly sales, daily temperature of a city and so on.
The input data must be a pandas.DataFrame format with two columns only: date (datetime format) and observed data (float or int format). The first column must be named as **date** and the second one could be named as you desire.

```python
import pandas as pd
data = pd.read_csv("tests/resource/stock_prices.csv")
filtered_data = data[['period','close']]
filtered_data.columns = ['date','close_price']
filtered_data = filtered_data.sort_values("date")
filtered_data["date"] = pd.to_datetime(filtered_data["date"])
```

Once some trend is identified, detectTrend provides period on trend, drawdown, maximum dradown, or buildup in case of uptrend and a plot with all trends found.


## Why detectTrend is important?

Detection of trends could be used in machine learning algorithms such as classification problems like binary (1 = uptrend, 0 = otherwise) or non-binary classifications (1 = uptrend, -1 = downtrend, 0 = otherwise). Besides that, could be used in prediction problems.

## Example

Inform:
 - type of trend you desire to investigate => downtrend or uptrend;
 - window or maximum period of a trend (example: 60 days considering 1 day as 1 period) **optional**;
 - minimum period that you consider a trend (default 5 periods) **optional**;
 - instead of minimum period, you may inform the quantile of time span such as 0.8 (80%).

```python
from detectTrend import detectTrend

trend = "downtrend"
stock = "close_price"
window = 126 #6 months

trends_detected, statistcs = detectTrend(filtered_data, trend=trend, window=window)
```

The variable `trends_detected` is a dataframe that contais the initial and end date of each trend, the prices of each date, time span of each trend and the drawdown of each trend. Let's see rhe first five rows of this dataframe:

```
| from                | to                  |   price0 |   price1 |   indice_from |   indice_to |   time_span |   drawdown |
|:--------------------|:--------------------|---------:|---------:|--------------:|------------:|------------:|-----------:|
| 2000-01-03 00:00:00 | 2000-01-31 00:00:00 |  5.90057 |  5.12252 |             0 |          19 |          19 |  0.131859  |
| 2000-03-09 00:00:00 | 2000-04-24 00:00:00 |  6.42701 |  5.02208 |            45 |          76 |          31 |  0.218597  |
| 2000-05-02 00:00:00 | 2000-05-11 00:00:00 |  5.53684 |  5.29352 |            81 |          88 |           7 |  0.0439456 |
| 2000-05-16 00:00:00 | 2000-05-24 00:00:00 |  5.59962 |  5.24807 |            91 |          97 |           6 |  0.0627803 |
| 2000-06-08 00:00:00 | 2000-06-15 00:00:00 |  6.30359 |  6.1646  |           108 |         113 |           5 |  0.0220487 |
```

The output statistcs shows the basic statistics such as: minimum, maximum (must be equal to window variable) and other percentiles of all periods of trends.
This is important if you want to cut all small trends detected. By default, the limit variable cut off all trends with 5 periods detected. 
The statistcs exhibit all trend with no cut off at all.

Let's see the statistcs:

```
|       |   time_span |
|:------|------------:|
| count |   2444      |
| mean  |     12.5569 |
| std   |     26.0989 |
| min   |      1      |
| 25%   |      1      |
| 50%   |      2      |
| 75%   |      8      |
| 80%   |     12      |
| 85%   |     18.55   |
| 90%   |     33      |
| 92.5% |     57.775  |
| 95%   |     88      |
| 97.5% |    110      |
| 99%   |    122      |
| max   |    126      |
```

As we just saw, the median (50% percentile) shows that 50% of trends is just 2 periods (2 days in this case), therefore the default limit of 5 it is a good cut number.
Next, we will redefine the limit value with 21 periods.

The easiest way to vizualize the trends detected, just call `plot_trend` function.
All trends detected, with maximum window informed and the minimum informed by the limit value, will be displayed.

```python
from detectTrend import plot_trend
plot_trend(filtered_data, trends_detected, stock, trend)
```
<center>
<img src="https://github.com/rafa-rod/detectTrend/blob/main/media/plot_trend_whole_serie.png" style="width:60%;"/>
</center>

It is also possible to filter data by informing year variable. In this example, the series contains data after year 2005.

```python
year = 2005

trends_detected, _ = detectTrend(filtered_data, trend=trend, limit=21,
                                      window=janela, year=year)

#same:
trends_detected, _ = detectTrend(filtered_data, trend=trend, quantile=0.85,
                                      window=janela, year=year)
```
<center>
<img src="https://github.com/rafa-rod/detectTrend/blob/main/media/plot_trend.png" style="width:60%;"/>
</center>

The maximum drawdown it is calculate by call function `maxdradown` returning: peak and valley values, data in which they occurred and the maxdrawdown value.

```python
from detectTrend import maxdradown
maxdd = maxdradown(filtered_data, trends_detected, year) 
```

```
|   peak_price |   valley_price | peak_date_maxdrawdown   | valley_date_maxdrawdown   |   maxdrawdown | time_span          |
|-------------:|---------------:|:------------------------|:--------------------------|--------------:|:-------------------|
|        52.51 |            4.2 | 2008-05-21 00:00:00     | 2016-01-26 00:00:00       |      0.920015 | 2806 days 00:00:00 |
```

To exhibit the maximium drawdown of the time series just call `plot_maxdrawdown` function and select the style of the plot: shadow, area or plotly.

```python
from detectTrend import plot_maxdrawdown
plot_maxdrawdown(filtered_data, maxdd, stock, trend, year, style="shadow")
```

<center>
<img src="https://github.com/rafa-rod/detectTrend/blob/main/media/maxdd_shadow.png" style="width:60%;"/>
</center>


```python
from detectTrend import plot_maxdrawdown
plot_maxdrawdown(filtered_data, maxdd, stock, trend, year, style="area")
```

<center>
<img src="https://github.com/rafa-rod/detectTrend/blob/main/media/maxdd_area.png" style="width:60%;"/>
</center>


If you select plotly style, you must install `plotly` package:

```bash
pip install plotly
```

```python
from detectTrend import plot_maxdrawdown
plot_maxdrawdown(filtered_data, maxdd, stock, trend, year, style="plotly")
```

<center>
<img src="https://github.com/rafa-rod/detectTrend/blob/main/media/maxdd_plotly.png" style="width:60%;"/>
</center>

