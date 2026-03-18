import os
import sys

import pandas as pd
import pytest

sys.path.append("./src/pytrendseries")
path2 = os.path.join("./tests/resource")

import detecttrend
import maximum_drawdown as mdd
import time_under_water as tuw
import vizplot
from detecttrend import get_trends_labels


class TestClass:
    def setup_method(self):
        """Setup configurations executed before each test"""
        self.year = 2020
        self.trend = "downtrend"
        self.window = 30
        prices = pd.read_csv(os.path.join(path2, "stock_prices.csv"), index_col=0)
        prices = prices[["period", "close"]].set_index("period")
        prices = prices.rename(columns={"close": "close_price"})
        prices.index = pd.to_datetime(prices.index)
        prices = prices.sort_index()

        self.df_prices = prices
        self.price = self.df_prices.values
        self.output1 = None
        self.output1_1 = None
        self.output2 = None
        self.output3 = None
        self.output4 = None
        self.output_mdd = None
        self.output_tuw = None

    # ==================== DETECT TREND TESTS ====================
    def test_detecttrend(self):
        """Test original detecttrend function"""
        output1 = detecttrend.detecttrend(
            self.df_prices, trend=self.trend, window=self.window
        )
        self.output1 = output1
        assert (output1["Peak Date"] < output1["Valley Date"]).all()
        assert (output1["Peak"] > output1["Valley"]).all()

        output1_1 = detecttrend.detecttrend(
            self.df_prices, trend="uptrend", window=self.window
        )
        self.output1_1 = output1_1
        assert (output1_1["Valley Date"] < output1_1["Peak Date"]).all()
        assert (output1_1["Valley"] < output1_1["Peak"]).all()

    # ==================== MAX DRAWDOWN TESTS ====================
    def test_maxdrawdown_optimized(self):
        """Test optimized maxdrawdown function from maximum_drawdown.py"""
        # Global MDD (no window)
        output_mdd = mdd.maxdrawdown(self.df_prices, window=None, verbose=False)
        self.output_mdd = output_mdd

        # Validate structure
        assert not output_mdd.empty, "Result should not be empty"
        assert "MaxDD" in output_mdd.columns
        assert "Time Span" in output_mdd.columns
        assert "Peak Date" in output_mdd.columns
        assert "Valley Date" in output_mdd.columns
        assert "Window Start" in output_mdd.columns
        assert "Window End" in output_mdd.columns

        # Validate data integrity
        assert (output_mdd["Peak Date"] <= output_mdd["Valley Date"]).all(), (
            "Peak Date must be before or equal to Valley Date"
        )
        assert (output_mdd["Peak"] >= output_mdd["Valley"]).all(), (
            "Peak value must be greater than or equal to Valley value"
        )
        assert (output_mdd["MaxDD"] >= 0).all(), "MaxDD must be non-negative"
        assert (output_mdd["Time Span"] > 0).all(), "Time Span must be positive"

        # Validate MaxDD calculation (should be between 0 and 1)
        assert (output_mdd["MaxDD"] <= 1).all(), "MaxDD should not exceed 100%"

    def test_maxdrawdown_with_window(self):
        """Test maxdrawdown with window parameter"""
        output_window = mdd.maxdrawdown(self.df_prices, window=252, verbose=False)

        assert not output_window.empty, "Result should not be empty"
        assert len(output_window) >= 1, "Should have at least one window"

        # Validate all rows
        assert (output_window["Time Span"] > 0).all(), "All Time Spans must be positive"
        assert (output_window["MaxDD"] >= 0).all(), (
            "All MaxDD values must be non-negative"
        )

        output_sorted = output_window.sort_values("Window Start").reset_index(drop=True)
        # Check window boundaries are sequential (not overlapping)
        if len(output_sorted) > 1:
            for i in range(len(output_sorted) - 1):
                # Window End of row i should be before Window Start of row i+1
                # (non-overlapping windows)
                assert (
                    output_sorted.iloc[i]["Window End"]
                    < output_sorted.iloc[i + 1]["Window Start"]
                ), "Windows should not overlap"

    def test_maxdrawdown_edge_cases(self):
        """Test maxdrawdown with edge cases"""
        # Empty DataFrame - should handle gracefully
        df_empty = pd.DataFrame({"close": []}, index=pd.to_datetime([]))
        with pytest.raises(ValueError) as exc_info:
            mdd.maxdrawdown(df_empty, verbose=False)
        assert "Input must be a dataframe" in str(exc_info.value)

        # Single row - should return empty
        df_single = pd.DataFrame({"close": [100]}, index=pd.to_datetime(["2020-01-01"]))
        result_single = mdd.maxdrawdown(df_single, verbose=False)
        assert result_single.empty, "Single row should return empty DataFrame"

        # Only increasing prices (no drawdown)
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        prices_increasing = pd.DataFrame({"close": range(100, 110)}, index=dates)
        result_increasing = mdd.maxdrawdown(prices_increasing, verbose=False)
        # Should be empty or have MaxDD = 0
        if not result_increasing.empty:
            assert (result_increasing["MaxDD"] == 0).all(), (
                "Increasing prices should have zero drawdown"
            )

    def test_maxdrawdown_window_size_validation(self):
        """Test maxdrawdown window parameter validation"""
        # Window larger than data should work (treats as global)
        result_large = mdd.maxdrawdown(self.df_prices, window=10000, verbose=False)
        assert not result_large.empty, "Large window should work (global calculation)"

        # Window = None should work (global calculation)
        result_none = mdd.maxdrawdown(self.df_prices, window=None, verbose=False)
        assert not result_none.empty, "None window should work (global calculation)"

    # ==================== TIME UNDER WATER TESTS ====================
    def test_time_under_water_optimized(self):
        """Test optimized time_under_water function"""
        output_tuw = tuw.calculate_time_under_water(self.df_prices, verbose=False)
        self.output_tuw = output_tuw

        if not output_tuw.empty:
            # Validate structure - CORRECTED COLUMN NAMES
            assert "Peak Date" in output_tuw.columns
            assert "Recovery Date" in output_tuw.columns  # NOT "Valley Date"
            assert "Time Underwater" in output_tuw.columns
            assert "Status" in output_tuw.columns
            assert "MaxDD" in output_tuw.columns
            assert "Valley" in output_tuw.columns  # Valley value, not date

            # Validate data integrity
            assert (output_tuw["Peak"] > output_tuw["Valley"]).all(), (
                "Peak value must be greater than Valley value"
            )
            assert (output_tuw["MaxDD"] > 0).all(), (
                "MaxDD must be positive for drawdown periods"
            )
            assert (output_tuw["Time Underwater"] > 0).all(), (
                "Time Underwater must be positive (NO NEGATIVE VALUES)"
            )

            # Validate Status column
            valid_statuses = {"Recovered", "Ongoing"}
            assert set(output_tuw["Status"].unique()).issubset(valid_statuses), (
                f"Status must be one of {valid_statuses}"
            )

            # Validate Recovery Date consistency with Status
            recovered = output_tuw[output_tuw["Status"] == "Recovered"]
            ongoing = output_tuw[output_tuw["Status"] == "Ongoing"]

            if len(recovered) > 0:
                assert (recovered["Peak Date"] < recovered["Recovery Date"]).all(), (
                    "Peak Date must be before Recovery Date"
                )
            if len(ongoing) > 0:
                assert ongoing["Recovery Date"].isna().all(), (
                    "Ongoing periods should have NaT Recovery Date"
                )

    def test_time_under_water_edge_cases(self):
        """Test time_under_water with edge cases"""
        # Empty DataFrame - should handle gracefully
        df_empty = pd.DataFrame({"close": []}, index=pd.to_datetime([]))
        with pytest.raises(ValueError) as exc_info:
            tuw.calculate_time_under_water(df_empty, verbose=False)
        assert "Input must be a dataframe" in str(exc_info.value)

        # Single row - should return empty
        df_single = pd.DataFrame({"close": [100]}, index=pd.to_datetime(["2020-01-01"]))
        result_single = tuw.calculate_time_under_water(df_single, verbose=False)
        assert result_single.empty, "Single row should return empty DataFrame"

        # Only increasing prices (no drawdown)
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        prices_increasing = pd.DataFrame({"close": range(100, 110)}, index=dates)
        result_increasing = tuw.calculate_time_under_water(
            prices_increasing, verbose=False
        )
        assert result_increasing.empty, (
            "Increasing prices should have no underwater periods"
        )

    def test_time_under_water_no_negative_values(self):
        """Critical test: Ensure NO negative Time Underwater values"""
        output_tuw = tuw.calculate_time_under_water(self.df_prices, verbose=False)

        if not output_tuw.empty:
            # This was the bug we fixed - ensure it never happens again
            assert (output_tuw["Time Underwater"] >= 0).all(), (
                "CRITICAL: Time Underwater cannot be negative!"
            )
            assert (output_tuw["Time Underwater"] > 0).all(), (
                "Time Underwater must be at least 1 period"
            )

            # Additional sanity checks
            min_tuw = output_tuw["Time Underwater"].min()
            assert min_tuw >= 1, (
                f"Minimum Time Underwater should be >= 1, got {min_tuw}"
            )

    def test_time_under_water_original_backward_compatibility(self):
        """Test backward compatibility - tuw() alias for calculate_time_under_water()"""
        # Check if tuw() function exists (backward compatibility)
        if hasattr(tuw, "tuw"):
            output4 = tuw.tuw(self.df_prices)
        else:
            # Use the new function name
            output4 = tuw.calculate_time_under_water(self.df_prices, verbose=False)

        if not output4.empty:
            assert (
                "Time Underwater" in output4.columns
                or "time underwater" in output4.columns
            )
            # Original test assertion
            assert int(output4.iloc[0]["Time Underwater"]) >= 0, (
                "Original TUW should have non-negative time underwater"
            )

    # ==================== ORIGINAL TESTS (UPDATED) ====================
    def test_maxdrawdown_original(self):
        """Test maxdrawdown function (updated to use correct module)"""
        # CORRECTED: maxdrawdown is in maximum_drawdown module, not detecttrend
        output2 = mdd.maxdrawdown(self.df_prices, verbose=False)
        self.output2 = output2
        assert output2.shape[0] >= 1, "Should have at least one result"

        output3 = mdd.maxdrawdown(self.df_prices, window=252, verbose=False)
        self.output3 = output3
        assert output3.shape[0] >= 1, "Should have at least one window result"

        # Validate column names match expected
        assert "MaxDD" in output2.columns
        assert "Peak Date" in output2.columns or "Date Peak" in output2.columns

    def test_tuw_original(self):
        """Test tuw function (updated to use correct function name)"""
        # CORRECTED: Use calculate_time_under_water instead of tuw()
        output4 = tuw.calculate_time_under_water(self.df_prices, verbose=False)
        self.output4 = output4
        if not output4.empty:
            assert "Time Underwater" in output4.columns
            assert int(output4["Time Underwater"].values[0]) >= 0

    def test_get_trends_labels(self):
        """Test get_trends_labels function"""
        df_labeled = get_trends_labels(self.df_prices.copy(), window=self.window)
        assert "label" in df_labeled.columns
        assert df_labeled.shape[0] == self.df_prices.shape[0]
        assert set(df_labeled["label"].unique()).issubset({-1, 0, 1})

        custom_labels = {"uptrend": "BUY", "downtrend": "SELL", "notrend": "HOLD"}
        df_custom = get_trends_labels(
            self.df_prices.copy(), labels=custom_labels, window=self.window
        )
        assert set(df_custom["label"].unique()).issubset({"BUY", "SELL", "HOLD"})

        binary_labels = {"uptrend": 1, "notrend": 0}
        df_binary = get_trends_labels(
            self.df_prices.copy(), labels=binary_labels, window=self.window
        )
        assert set(df_binary["label"].unique()).issubset({0, 1})

        assert df_labeled.index.equals(self.df_prices.index)
        assert "label" not in self.df_prices.columns

    def test_raises(self):
        """Test error handling and validation"""
        with pytest.raises(Exception) as error1:
            detecttrend.detecttrend(
                self.df_prices, trend=self.trend, window=self.window, limit="11"
            )
        with pytest.raises(Exception) as error2:
            detecttrend.detecttrend(
                self.df_prices, trend=self.trend, window=self.window, limit=11.2
            )
        with pytest.raises(Exception) as error6:
            detecttrend.detecttrend(self.df_prices, trend=self.trend, window=0)
        with pytest.raises(Exception) as error7:
            detecttrend.detecttrend(self.df_prices, trend=self.trend, window=4)
        with pytest.raises(Exception) as error8:
            detecttrend.detecttrend(self.df_prices, trend=self.trend, window=30.2)
        with pytest.raises(Exception) as error9:
            detecttrend.detecttrend(self.df_prices, trend=self.trend, window="30")
        with pytest.raises(Exception) as error13:
            detecttrend.detecttrend(self.df_prices, trend="test", window=self.window)
        with pytest.raises(Exception) as error14:
            detecttrend.detecttrend(self.df_prices, trend=1, window=self.window)
        with pytest.raises(Exception) as error18:
            detecttrend.detecttrend(
                pd.DataFrame(
                    [[1, 2, 3], [2, 4, 5]], columns=["date", "month", "sales"]
                ),
                trend=self.trend,
                window=self.window,
            )
        assert str(error1.value) == "Limit parameter must be a interger value."
        assert str(error2.value) == "Limit parameter must be a interger value."
        assert (
            str(error6.value)
            == "Window parameter must be a integer and greater than limit value (in days)."
        )
        assert (
            str(error7.value)
            == "Window parameter must be a integer and greater than limit value (in days)."
        )
        assert (
            str(error8.value)
            == "Window parameter must be a integer and greater than limit value (in days)."
        )
        assert (
            str(error9.value)
            == "Window parameter must be a integer and greater than limit value (in days)."
        )
        assert (
            str(error13.value)
            == "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
        )
        assert (
            str(error14.value)
            == "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
        )
        assert (
            str(error18.value)
            == "Input must be a dataframe containing one column and its index must be in datetime format."
        )

    # ==================== VISUALIZATION TESTS ====================
    def plots(self):
        """Visual tests (pytest does not capture, manual verification)"""
        vizplot.plot_trend(
            self.df_prices, self.output1, trend=self.trend, year=self.year
        )
        vizplot.plot_trend(
            self.df_prices, self.output1_1, trend="uptrend", year=self.year
        )
        vizplot.plot_drawdowns(
            self.df_prices,
            figsize=(10, 4),
            color="gray",
            alpha=0.6,
            title="Drawdowns",
            axis="y",
        )
        vizplot.plot_evolution(
            self.df_prices, figsize=(10, 4), colors=["gray", "red"], alphas=[1, 0.6]
        )
