
import pandas as pd
import numpy as np
import sys, os, pytest

path = "../pytrendseries/"
sys.path.append(path)

path2 = "../pytrendseries/tests/resource"
sys.path.append(path2)

import detecttrend
import maxtrend
import vizplot

class TestClass():

      def __init__(self):
            self.year = 2020
            self.trend = "downtrend"
            self.window = 30
            prices = pd.read_csv(os.path.join(path2, "stock_prices.csv"), index_col=0)
            prices = prices[["period",'close']]
            prices = prices.rename(columns={"period":"date", "close":"close_price"})
            prices["date"] = pd.to_datetime(prices["date"])

            self.df_prices = prices
            self.price = self.df_prices.values
            self.stock = 'close_price'
            self.test_detecttrend()
            self.test_max_trend()
            self.test_raises()
            self.plots()

      def test_detecttrend(self):
            output1, _ = detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=self.year)
            self.output1 = output1
            assert (output1["from"] < output1["to"]).unique().shape[0] == 1
            assert (output1["from"] < output1["to"]).unique()[0] == True
            assert (output1["price0"] > output1["price1"]).unique().shape[0] == 1
            assert (output1["price0"] > output1["price1"]).unique()[0] == True

            output1_1, _ = detecttrend.detecttrend(self.df_prices, trend="uptrend", window=self.window)
            assert (output1_1["from"] < output1_1["to"]).unique().shape[0] == 1
            assert (output1_1["from"] < output1_1["to"]).unique()[0] == True
            assert (output1_1["price0"] < output1_1["price1"]).unique().shape[0] == 1
            assert (output1_1["price0"] < output1_1["price1"]).unique()[0] == True

      def test_max_trend(self):
            output2 = maxtrend.getmaxtrend(self.df_prices, self.stock, self.trend, self.year)
            self.output2 = output2
            assert round(output2['maxdrawdown'].values[0], 5) == 0.63356
            assert round(maxtrend.getmaxtrend(self.df_prices, self.stock, 'uptrend', self.year)['maxrunup'].values[0], 5) == 1.75642
            assert output2.shape[0] == 1
            assert (output2["peak_date"] < output2["valley_date"]).unique()[0] == True
            assert (output2["peak_price"] > output2["valley_price"]).unique()[0] == True

      def plots(self):
      		vizplot.plot_trend(self.df_prices, self.output1, self.stock, trend=self.trend, year=self.year)
      		vizplot.plot_maxdrawdown(self.df_prices, self.output2, self.stock, trend=self.trend, year=self.year, style="shadow")
      		vizplot.plot_maxdrawdown(self.df_prices, self.output2, self.stock, trend=self.trend, year=self.year, style="area")
      		vizplot.plot_maxdrawdown(self.df_prices, self.output2, self.stock, trend=self.trend, year=self.year, style="plotly")

      def test_raises(self):
            with pytest.raises(Exception) as error1:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=self.year, limit='11')
            with pytest.raises(Exception) as error2:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=self.year, limit=11.2)
            with pytest.raises(Exception) as error3:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=self.year, quantile=2)
            with pytest.raises(Exception) as error4:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=self.year, quantile=2.3)
            with pytest.raises(Exception) as error5:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=self.year, quantile='0.5')
            with pytest.raises(Exception) as error6:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=0, year=self.year)
            with pytest.raises(Exception) as error7:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=4, year=self.year)
            with pytest.raises(Exception) as error8:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=30.2, year=self.year)
            with pytest.raises(Exception) as error9:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window='30', year=self.year)
            with pytest.raises(Exception) as error10:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=-1)
            with pytest.raises(Exception) as error11:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=2020.0)
            with pytest.raises(Exception) as error12:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year='2020')
            with pytest.raises(Exception) as error13:
                  detecttrend.detecttrend(self.df_prices, trend='test', window=self.window, year=self.year)
            with pytest.raises(Exception) as error14:
                  detecttrend.detecttrend(self.df_prices, trend=1, window=self.window, year=self.year)
            with pytest.raises(Exception) as error15:
                  detecttrend.detecttrend([1,2,3,4], trend=self.trend, window=self.window, year=self.year)
            with pytest.raises(Exception) as error16:
                  detecttrend.detecttrend(pd.DataFrame([1,2,3]), trend=self.trend, window=self.window, year=self.year)
            with pytest.raises(Exception) as error17:
                  detecttrend.detecttrend(pd.DataFrame([1,2,3],columns=["date"]), trend=self.trend, window=self.window, year=self.year)
            with pytest.raises(Exception) as error18:
                  detecttrend.detecttrend(pd.DataFrame([[1,2,3],[2,4,5]],columns=["date",'month','sales']), trend=self.trend, window=self.window, year=self.year)
            with pytest.raises(Exception) as error19:
                  detecttrend.detecttrend(self.df_prices, trend=self.trend, window=self.window, year=self.year, limit=5, quantile=0.8)
            assert str(error1.value) == "Limit parameter must be a interger value."
            assert str(error2.value) == "Limit parameter must be a interger value."
            assert str(error3.value) == "Quantile parameter must be a float value between 0-1."
            assert str(error4.value) == "Quantile parameter must be a float value between 0-1."
            assert str(error5.value) == "Quantile parameter must be a float value between 0-1."
            assert str(error6.value) == "Window parameter must be a integer and greater than limit value (in days)."
            assert str(error7.value) == "Window parameter must be a integer and greater than limit value (in days)."
            assert str(error8.value) == "Window parameter must be a integer and greater than limit value (in days)."
            assert str(error9.value) == "Window parameter must be a integer and greater than limit value (in days)."
            assert str(error10.value) == "Year parameter must be a integer value."
            assert str(error11.value) == "Year parameter must be a integer value."
            assert str(error12.value) == "Year parameter must be a integer value."
            assert str(error13.value) == "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
            assert str(error14.value) == "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
            assert str(error15.value) == "Input must be a dataframe containing two columns, one of them called 'date' in datetime format."
            assert str(error16.value) == "Input must be a dataframe containing two columns, one of them called 'date' in datetime format."
            assert str(error17.value) == "Input must be a dataframe containing two columns, one of them called 'date' in datetime format."
            assert str(error18.value) == "Input must be a dataframe containing two columns, one of them called 'date' in datetime format."
            assert str(error19.value) == "Choose just one parameter (quantile or limit)."

TestClass()