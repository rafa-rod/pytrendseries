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
    <a href="https://pepy.tech/projects/pytrendseries">
        <img src="https://static.pepy.tech/badge/pytrendseries" alt="PyPI Downloads">
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
filtered_data = filtered_data.sort_index()
```

Once some trend is identified, **pytrendseries** provides period on trend, drawdown, maximum drawdown (or drawup in case of uptrend) and a plot with all trends found.

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
 - window or maximum period of a trend (example: 60 days considering 1 day as 1 period);
 - the minimum value that represents the number of consecutive days (or another period of time) to be considered a trend (default 5 periods).

```python
import pytrendseries

trend = "downtrend"
window = 126 #6 months

trends_detected = pytrendseries.detecttrend(filtered_data, trend=trend, window=window)
```

The variable `trends_detected` is a dataframe that contains the initial and end date of each trend, the prices of each date, time span of each trend and the drawdown of each trend. Let's see the first five rows of this dataframe:

```
| Peak Date           | Valley Date         |   Peak   |   Valley |   index_peak  |index_valley |   time_span |   drawdown |
|:--------------------|:--------------------|---------:|---------:|--------------:|------------:|------------:|-----------:|
| 2000-01-03 00:00:00 | 2000-01-31 00:00:00 |  5.90057 |  5.12252 |             0 |          19 |          19 |  0.131859  |
| 2000-03-09 00:00:00 | 2000-04-24 00:00:00 |  6.42701 |  5.02208 |            45 |          76 |          31 |  0.218597  |
| 2000-05-02 00:00:00 | 2000-05-11 00:00:00 |  5.53684 |  5.29352 |            81 |          88 |           7 |  0.0439456 |
| 2000-05-16 00:00:00 | 2000-05-24 00:00:00 |  5.59962 |  5.24807 |            91 |          97 |           6 |  0.0627803 |
| 2000-06-08 00:00:00 | 2000-06-15 00:00:00 |  6.30359 |  6.1646  |           108 |         113 |           5 |  0.0220487 |
```

The easiest way to vizualize the trends detected, just call `plot_trend` function.
All trends detected, with maximum window informed and the minimum informed by the limit value, will be displayed.

```python
import pytrendseries
trend = "downtrend"
window = 30
year = 2020

trends_detected = pytrendseries.detecttrend(filtered_data, trend=trend, window=window)
pytrendseries.vizplot.plot_trend(filtered_data, trends_detected, trend, year)
```
<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/plot_downtrend.png" style="width:90%;"/>
</center>

To visualize all uptrends found, inform `trend='uptrend'`:

```python
import pytrendseries
window = 30
year = 2020

trends_detected = pytrendseries.detecttrend(filtered_data, trend='uptrend', window=window)
pytrendseries.vizplot.plot_trend(filtered_data, trends_detected, 'uptrend', year)
```

 <center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/plot_uptrend.png" style="width:90%;"/>
</center>

The maximum drawdown or maximum drawup can be obtained by sorting the dataframe by column drawdown. To do that, just code:

```python
maxdd_in_window = trends_detected.sort_values("drawdown", ascending=False).iloc[0:1]
```

Another way is to call the function `maxdrawdown`. Note that this result will be differente once the maximum drawdown of the intire timeseries.

```python
maxdd = pytrendseries.maxdrawdown(filtered_data)
```

You can code to vizualize as follows:

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(14,5))
plt.plot(filtered_data, alpha=0.6)
location_x = maxdd.values[:,0]
location_y = maxdd.values[:,1]
for i in range(location_x.shape[0]):
    plt.axvspan(location_x[i], location_y[i], alpha=0.3, color="red")
plt.grid(axis='x')
plt.show()
```

<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/maxdd.png" style="width:90%;"/>
</center>

You may pass the parameter window to obtain the same result:

```python
maxdd_in_window = pytrendseries.maxdrawdown(filtered_data, window=252)
```

To vizualize all drawdowns of timeseries, call the following function:

```python
import pytrendseries
pytrendseries.plot_drawdowns(filtered_data, figsize = (10,4), color="gray", alpha=0.6, title="Drawdowns", axis="y")
```

<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/plot_drawdons.png" style="width:90%;"/>
</center>

Another option is:

```python
import pytrendseries
pytrendseries.plot_evolution(filtered_data, figsize = (10,4), colors=["gray", "red"], alphas=[1,0.6])
```

<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/plot_evolution.png" style="width:90%;"/>
</center>


To get time underwater (tuw), just type:

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

The table shows time underwater as NaN, it means that the timeseries still on downtrend.

Another important usage of `pytrendseries` is to obtain the series of drawdowns or series of maximum drawdowns in order to calculate the drawdown at risk or maximum drawdown at risk.


```python
import pytrendseries
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_style("white")

trend = "downtrend"
window = 126 #6 months

trends_detected = pytrendseries.detecttrend(filtered_data, trend=trend, window=window)

plt.figure(figsize=(15,5))
sns.histplot(trends_detected["drawdown"]*100, kde=True, bins=30)
plt.ylabel("")
plt.box(False)
plt.annotate('Maximum Drawdown', xy=((trends_detected["drawdown"].max()-0.005)*100, 1),
             xycoords='data',
            xytext=(-105, 30), textcoords='offset points',color="red",
            weight='bold',
            arrowprops=dict(arrowstyle="->", color="r",
                            connectionstyle='arc3,rad=-0.1'))
plt.annotate('Quantile 97,5%', xy=((trends_detected["drawdown"].quantile(0.975)-0.005)*100, 0.2),
             xycoords='data',
            xytext=(-135, 30), textcoords='offset points',color="red",
            weight='bold',
            arrowprops=dict(arrowstyle="->", color="r",
                            connectionstyle='arc3,rad=-0.1'))
plt.xlabel("Drawdown (%)")
plt.ylabel("Density", rotation=0, labelpad=-30, loc="top")
plt.show()
```

<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/series_drawdown.png" style="width:90%;"/>
</center>


```python
import pytrendseries
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_style("white")

maxdd_in_window = maxdrawdown(filtered_data, window=126)

plt.figure(figsize=(15,5))
sns.histplot(maxdd_in_window["MaxDD"]*100, kde=True, bins=30)
plt.ylabel("")
plt.box(False)
plt.annotate('Maximum Drawdown', xy=((maxdd_in_window["MaxDD"].max()-0.005)*100, 1),
             xycoords='data',
            xytext=(-105, 30), textcoords='offset points',color="red",
            weight='bold',
            arrowprops=dict(arrowstyle="->", color="r",
                            connectionstyle='arc3,rad=-0.1'))
plt.annotate('Quantile 95%', xy=((maxdd_in_window["MaxDD"].quantile(0.95)-0.005)*100, 0.2),
             xycoords='data',
            xytext=(-135, 50), textcoords='offset points',color="red",
            weight='bold',
            arrowprops=dict(arrowstyle="->", color="r",
                            connectionstyle='arc3,rad=-0.1'))
plt.xlabel("Maximum Drawdowns (%)")
plt.ylabel("Density", rotation=0, labelpad=-30, loc="top")
plt.show()
```

<center>
<img src="https://github.com/rafa-rod/pytrendseries/blob/main/media/series_max_drawdown.png" style="width:90%;"/>
</center>

# Trend Labeling for Machine Learning

The `get_trends_labels` function automates the process of labeling financial time series data based on detected market structures. By identifying peaks and valleys within a specified window, it segments the data into **Uptrends**, **Downtrends**, and **No Trend** periods.

## Why use this for Machine Learning?

This function is particularly useful for **supervised learning classification problems**. Instead of trying to predict the exact future price (a regression problem), you can train models to predict the market state or direction.

*   **Target Variable Engineering:** Converts raw price data into discrete classes (e.g., `1`, `-1`, `0`).
*   **Noise Reduction:** Ignores minor fluctuations by focusing on significant trends defined by the `window` and `limit` parameters.
*   **Flexibility:** Allows custom labeling schemes (e.g., numeric for models, strings for interpretability).

## Output Example

After running the function, your dataframe will include a new `label` column indicating the market regime for each date.

| Date | Close | Label | Market State |
| :--- | :--- | :---: | :--- |
| 2023-01-03 | 100.5 | 0 | No Trend |
| 2023-01-04 | 101.2 | 0 | No Trend |
| 2023-01-05 | 103.5 | **1** | **Uptrend** |
| 2023-01-06 | 105.0 | **1** | **Uptrend** |
| 2023-01-09 | 104.8 | **1** | **Uptrend** |
| 2023-01-10 | 102.0 | 0 | No Trend |
| 2023-01-11 | 99.5 | **-1** | **Downtrend** |
| 2023-01-12 | 98.0 | **-1** | **Downtrend** |

## Usage Examples

### 1. Default Configuration
Uses standard numeric labels (`1` for uptrend, `-1` for downtrend, `0` for no trend).

```python
df_labeled = get_trends_labels(df, window=252, limit=5)
```
### 2. Custom String Labels
Useful for interpretability or specific model requirements.

```python
custom_labels = {
    "uptrend": "BUY", 
    "downtrend": "SELL", 
    "notrend": "HOLD"
}
df_labeled = get_trends_labels(df, labels=custom_labels)
```

### 3. Binary Classification (Uptrend vs. Rest)
Ignore downtrends and treat them as "no trend" for a specific strategy.

```python
binary_labels = {
    "uptrend": 1, 
    "notrend": 0
}
df_labeled = get_trends_labels(df, labels=binary_labels)
```


