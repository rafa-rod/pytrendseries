
import pandas as pd
import numpy as np
import sys, os, pytest

path = "../pytrendseries/"
sys.path.append(path)

path2 = "../pytrendseries/tests/resource"
sys.path.append(path2)

import detecttrend
import vizplot
import time_under_water as tuw

class TestClass():

      def __init__(self):
            self.year = 2020
            self.trend = "downtrend"
            self.window = 30
            prices = pd.read_csv(os.path.join(path2, "stock_prices.csv"), index_col=0)
            prices = prices[["period",'close']].set_index("period")
            prices = prices.rename(columns={"close":"close_price"})
            prices.index = pd.to_datetime(prices.index)
            prices = prices.sort_index()

            self.df_prices = prices
            self.price = self.df_prices.values
            self.test_detecttrend()
            self.test_max_trend()
            self.test_raises()
            self.plots()

      def test_detecttrend(self):
            output1 = detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window)
            self.output1 = output1
            assert (output1["from"] < output1["to"]).unique().shape[0] == 1
            assert (output1["from"] < output1["to"]).unique()[0] == True
            assert (output1["price0"] > output1["price1"]).unique().shape[0] == 1
            assert (output1["price0"] > output1["price1"]).unique()[0] == True

            output1_1 = detecttrend.detecttrend(self.df_prices, trend="uptrend", window=self.window)
            self.output1_1 = output1_1
            assert (output1_1["from"] < output1_1["to"]).unique().shape[0] == 1
            assert (output1_1["from"] < output1_1["to"]).unique()[0] == True
            assert (output1_1["price0"] < output1_1["price1"]).unique().shape[0] == 1
            assert (output1_1["price0"] < output1_1["price1"]).unique()[0] == True

      def test_maxdrawdown(self):
            output2 = detecttrend.maxdrawdown(self.df_prices)
            self.output2 = output2
            assert round(output2['MaxDD'].values[0], 5) == 0.92002
            assert output2.shape[0] == 1
            assert (output2["Date Peak"] < output2["Date Valley"]).unique()[0] == True
            output3 = detecttrend.maxdrawdown(self.df_prices, self.window)
            self.output3 = output3
            assert round(output3['MaxDD'].values[0], 5) == 0.70793

      def test_tuw(self):
            output4 = tuw.tuw(self.df_prices)
            self.output4 = output4
            assert int(self.output4['time underwater'].values[0]) == 42       

      def plots(self):
            vizplot.plot_trend(self.df_prices, self.output1, trend=self.trend, year=self.year)
            vizplot.plot_trend(self.df_prices, self.output1_1, trend="uptrend", year=self.year)
            vizplot.plot_drawdowns(self.df_prices, figsize = (10,4), color="gray", alpha=0.6, title="Drawdowns", axis="y")
            vizplot.plot_evolution(self.df_prices, figsize = (10,4), colors=["gray", "red"], alphas=[1,0.6])

      def test_raises(self):
            with pytest.raises(Exception) as error1:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, limit='11')
            with pytest.raises(Exception) as error2:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, limit=11.2)
            with pytest.raises(Exception) as error6:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=0)
            with pytest.raises(Exception) as error7:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=4)
            with pytest.raises(Exception) as error8:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=30.2)
            with pytest.raises(Exception) as error9:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window='30')
            with pytest.raises(Exception) as error13:
                  detecttrend.detecttrend(self.df_prices, trend='test', window=self.window)
            with pytest.raises(Exception) as error14:
                  detecttrend.detecttrend(self.df_prices, trend=1, window=self.window)
            with pytest.raises(Exception) as error18:
                  detecttrend.detecttrend(pd.DataFrame([[1,2,3],[2,4,5]],columns=["date",'month','sales']), trend=self.trend, window=self.window)
            assert str(error1.value) == "Limit parameter must be a interger value."
            assert str(error2.value) == "Limit parameter must be a interger value."
            assert str(error6.value) == "Window parameter must be a integer and greater than limit value (in days)."
            assert str(error7.value) == "Window parameter must be a integer and greater than limit value (in days)."
            assert str(error8.value) == "Window parameter must be a integer and greater than limit value (in days)."
            assert str(error9.value) == "Window parameter must be a integer and greater than limit value (in days)."
            assert str(error13.value) == "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
            assert str(error14.value) == "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
            assert str(error18.value) == "Input must be a dataframe containing one column and its index must be in datetime format."

TestClass()