<p align="center">
  <img width=60% src="https://github.com/rafa-rod/pytrendseries/blob/main/media/maxdd_area.png">
</p>

<!-- buttons -->
<p align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-v3-brightgreen.svg"
            alt="python"></a> &nbsp;
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg"
            alt="MIT license"></a> &nbsp;
      <a href="https://codecov.io/gh/rafa-rod/detecttrend">
        <img src="https://codecov.io/gh/rafa-rod/detecttrend/branch/main/graph/badge.svg?token=98EMCTZTOY"/>
      </a>
</p>

<!-- content -->

**pytrendseries** is a Python library for detection of trends in time series like: stock prices, monthly sales, daily temperature of a city and so on.
The input data must be a `pandas.DataFrame` format containing one column as observed data (in float or int format). Follow example below:

```python
import pandas as pd
data = pd.read_csv("tests/resource/stock_prices.csv")
filtered_data = data[['period','close']].set_index("period")
filtered_data.columns = ['close_price']
filtered_data.index = pd.to_datetime(filtered_data.index)
filtered_data.index = filtered_data.sort_index()
```

Once some trend is identified, **pytrendseries** provides period on trend, drawdown, maximum drawdown (or buildup in case of uptrend) and a plot with all trends found.

## Installation

### Using pip

You can install using the pip package manager by running:

```sh
pip install pytrendseries
```

Alternatively, you could install the latest version directly from Github:

```sh
pip install https://github.com/rafa-rod/pytrendseries/archive/refs/heads/main.zip
```

## Why pytrendseries is important?

Detection of trends could be used in machine learning algorithms such as classification problems like binary (1 = uptrend, 0 = otherwise) or non-binary classifications (1 = uptrend, -1 = downtrend, 0 = otherwise). Besides that, could be used in prediction problems.

## Example

Inform:
 - type of trend you desire to investigate => downtrend or uptrend;
 - window or maximum period of a trend (example: 60 days considering 1 day as 1 period) **optional**;
 - the minimum value that represents the number of consecutive days (or anohter period of time) to be considered a trend (default 5 periods) **optional**;
 - instead of minimum period, you may inform the quantile of time span (consecutive days in trend) such as 0.8 (80%).

```python
import pytrendseries

trend = "downtrend"
window = 126 #6 months

trends_detected, statistcs = pytrendseries.detecttrend(filtered_data, trend=trend, window=window)
```

The variable `trends_detected` is a dataframe that contains the initial and end date of each trend, the prices of each date, time span of each trend and the drawdown of each trend. Let's see the first five rows of this dataframe:

```
| from                | to                  |   price0 |   price1 |   indice_from |   indice_to |   time_span |   drawdown |
|:--------------------|:--------------------|---------:|---------:|--------------:|------------:|------------:|-----------:|
| 2000-01-03 00:00:00 | 2000-01-31 00:00:00 |  5.90057 |  5.12252 |             0 |          19 |          19 |  0.131859  |
| 2000-03-09 00:00:00 | 2000-04-24 00:00:00 |  6.42701 |  5.02208 |            45 |          76 |          31 |  0.218597  |
| 2000-05-02 00:00:00 | 2000-05-11 00:00:00 |  5.53684 |  5.29352 |            81 |          88 |           7 |  0.0439456 |
| 2000-05-16 00:00:00 | 2000-05-24 00:00:00 |  5.59962 |  5.24807 |            91 |          97 |           6 |  0.0627803 |
| 2000-06-08 00:00:00 | 2000-06-15 00:00:00 |  6.30359 |  6.1646  |           108 |         113 |           5 |  0.0220487 |
```

The output `statistcs` shows the basic statistics such as: minimum, maximum (must be equal to window variable) and other percentiles of all periods of trends.
This is important if you want to filter all small and unnecessary trends detected such as: trend with only 2 consecutive days. By default, the limit variable cut off all trends with 5 periods found. 
The statistcs exhibit all trend with no cut off at all.

Let's see the `statistcs`:

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
import pytrendseries
pytrendseries.vizplot.plot_trend(filtered_data, trends_detected, trend)
```
<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/plot_trend_whole_serie.png" style="width:60%;"/>
</center>

It is also possible to filter data by informing year variable. In this example, the series contains data after year 2005.

```python
year = 2005

trends_detected, _ = pytrendseries.detecttrend(filtered_data, trend=trend, limit=21,
                                      window=janela, year=year)

#same:
trends_detected, _ = pytrendseries.detecttrend(filtered_data, trend=trend, quantile=0.85,
                                      window=janela, year=year)
```
<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/plot_trend.png" style="width:60%;"/>
</center>

To visualize all uptrends found, inform `trend='uptrend'`:

 <center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/plot_uptrend.png" style="width:60%;"/>
</center>

The maximum drawdown or maximum run up is calculate calling the function `max_trend` which return: peak and valley values, data in which they occurred and the maxdrawdown/maxrunup value.

```python
import pytrendseries
maxdd = pytrendseries.getmaxtrend(filtered_data, trend, year) 
```

```
|   peak_price |   valley_price | peak_date_maxdrawdown   | valley_date_maxdrawdown   |   maxdrawdown | time_span          |
|-------------:|---------------:|:------------------------|:--------------------------|--------------:|:-------------------|
|        52.51 |            4.2 | 2008-05-21 00:00:00     | 2016-01-26 00:00:00       |      0.920015 | 2806 days 00:00:00 |
```

Instead, you may want to known the maximum drawdown (maximum run up) according to informed window. To do that, just code:

```python
maxdd_in_window = trends_detected.sort_values("drawdown",ascending=False).iloc[0:1]
```

To exhibit the maximium drawdown of the time series just call `plot_maxdrawdown` function and select the style of the plot: shadow, area or plotly.

```python
import pytrendseries
pytrendseries.plot_maxdrawdown(filtered_data, maxdd, trend, year, style="shadow")
```

<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/maxdd_shadow.png" style="width:60%;"/>
</center>


```python
import pytrendseries
pytrendseries.plot_maxdrawdown(filtered_data, maxdd, trend, year, style="area")
```

<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/maxdd_area.png" style="width:60%;"/>
</center>


If you select plotly style, a interactive plot will be opened in your browser:

```python
import pytrendseries
pytrendseries.plot_maxdrawdown(filtered_data, maxdd, trend, year, style="plotly")
```

<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/maxdd_plotly.png" style="width:60%;"/>
</center>

To get time under water (tuw), just type:

```python
import pytrendseries
pytrendseries.tuw(filtered_data)
```

The output would be (showing the tail of the dataframe):

```
| inital_date|   peak    |   valley  |   drawdown  |   time underwater |   final_date |
|:-----------|----------:|----------:|------------:|------------------:|-------------:|
| 2007-12-28 |  44.66140 |  33.58194 |     0.24808 |                85 |   2008-05-06 |
| 2008-05-06 |  45.00000 |  44.85000 |     0.00333 |                4  |   2008-05-09 |
| 2008-05-13 |  46.95000 |  46.30000 |     0.01384 |                3  |   2008-05-15 |
| 2008-05-21 |  52.51000 |  4.20000  |     0.92002 |               NaN |          NaN |
```

The table show time underwater as NaN, it means that the timeseries still on downtrend.