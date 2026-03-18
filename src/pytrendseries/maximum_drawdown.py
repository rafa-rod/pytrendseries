import time
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from .detecttrend import *


def _calculate_max_drawdown_vectorized(prices_series: pd.Series) -> pd.DataFrame:
    """
    Calculates the Maximum Drawdown for a single series slice using vectorized operations.

    Parameters:
    -----------
    prices_series : pd.Series
        A time series of prices with a datetime index.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing a single row with the worst drawdown found,
        including the duration (Time Span) in number of periods.
    """
    if len(prices_series) < 2:
        return pd.DataFrame(
            columns=["Peak Date", "Valley Date", "Peak", "Valley", "MaxDD", "Time Span"]
        )

    # Convert to numpy arrays for performance
    prices = prices_series.to_numpy()
    dates = prices_series.index.to_numpy()

    # 1. Calculate the running peak (highest price seen so far)
    running_peak = np.maximum.accumulate(prices)

    # 2. Calculate drawdown at each point: (Price / Running Peak) - 1
    drawdown = (prices / running_peak) - 1

    # 3. Find the index of the maximum drawdown (minimum value in the drawdown series)
    valley_idx = np.argmin(drawdown)
    maxdd_value = abs(drawdown[valley_idx])

    # If no drawdown occurred (series only went up), return empty
    if maxdd_value == 0:
        return pd.DataFrame(
            columns=["Peak Date", "Valley Date", "Peak", "Valley", "MaxDD", "Time Span"]
        )

    # 4. Find the peak index that corresponds to this valley
    # The peak must occur before or at the same time as the valley
    peak_idx = np.argmax(running_peak[: valley_idx + 1])

    # 5. Calculate Time Span (number of periods/records from Peak to Valley)
    # Using indices is much faster than datetime masking and is frequency-agnostic
    time_span = int(valley_idx - peak_idx + 1)

    # 6. Construct the result DataFrame
    result = pd.DataFrame(
        [
            [
                dates[peak_idx],
                dates[valley_idx],
                prices[peak_idx],
                prices[valley_idx],
                maxdd_value,
                time_span,
            ]
        ],
        columns=["Peak Date", "Valley Date", "Peak", "Valley", "MaxDD", "Time Span"],
    )
    return result


def maxdrawdown(
    df_prices: Union[pd.DataFrame, pd.Series],
    window: Optional[int] = None,
    verbose: bool = True,
    **kwargs,
) -> pd.DataFrame:
    """
    Calculates the Maximum Drawdown within non-overlapping time windows.

    This function splits the time series into distinct windows of size 'window'
    and finds the single worst drawdown event within each window.

    Parameters:
    -----------
    df_prices : Union[pd.DataFrame, pd.Series]
        Time series of prices. Must have a datetime index.
        If DataFrame, the first column is used.
    window : Optional[int]
        Size of the window (number of records).
        Example: 252 for ~1 trading year, 21 for ~1 trading month.
        If None, calculates the global Maximum Drawdown for the entire series.
    verbose : bool
        If True, prints execution time and summary statistics.
    **kwargs : dict
        Additional arguments (e.g., 'format' for datetime parsing if needed).

    Returns:
    --------
    pd.DataFrame
        A DataFrame where each row represents a window, containing the
        worst drawdown found in that period and its duration (Time Span).
    """
    # 1. Validate and Prepare Index
    if not pd.api.types.is_datetime64_any_dtype(df_prices.index):
        df_prices.index = pd.to_datetime(df_prices.index, format=kwargs.get("format"))

    if window:
        _treat_parameters(df_prices, trend="downtrend", limit=1, window=window)
    else:
        _treat_parameters(df_prices, trend="downtrend", limit=1, window=1)

    # Normalize input to Series
    if isinstance(df_prices, pd.DataFrame):
        price_series = df_prices.iloc[:, 0]
    else:
        price_series = df_prices

    n = len(price_series)
    if n < 2:
        return pd.DataFrame(
            columns=[
                "Window Start",
                "Window End",
                "Peak Date",
                "Valley Date",
                "Peak",
                "Valley",
                "MaxDD",
                "Time Span",
            ]
        )

    # 2. Configure Window Size
    # If window is None or larger than data, treat as global calculation
    if window is None or window >= n:
        window = n

    start_time = time.time()
    results_list: List[pd.DataFrame] = []

    # 3. Loop over non-overlapping windows (step equals window size)
    for i in range(0, n, window):
        window_data = price_series.iloc[i : i + window]

        # Skip windows too small for calculation
        if len(window_data) < 2:
            continue

        dd_result = _calculate_max_drawdown_vectorized(window_data)

        if not dd_result.empty:
            # Add window context columns
            dd_result["Window Start"] = window_data.index[0]
            dd_result["Window End"] = window_data.index[-1]
            results_list.append(dd_result)

    # 4. Concatenate Results (Single operation outside the loop for performance)
    if results_list:
        result_df = pd.concat(results_list, ignore_index=True)
        result_df = result_df.sort_values("MaxDD", ascending=False).reset_index(
            drop=True
        )

        # Order columns for readability
        columns_order = [
            "Window Start",
            "Window End",
            "Peak Date",
            "Valley Date",
            "Peak",
            "Valley",
            "MaxDD",
            "Time Span",
        ]
        result_df = result_df[columns_order]
    else:
        result_df = pd.DataFrame(
            columns=[
                "Window Start",
                "Window End",
                "Peak Date",
                "Valley Date",
                "Peak",
                "Valley",
                "MaxDD",
                "Time Span",
            ]
        )

    if verbose:
        elapsed_time = time.time() - start_time
        n_windows = len(results_list)
        print(f"MDD calculated in {elapsed_time:.3f} seconds")
        print(f"Window Size: {window} records | Total Windows Analyzed: {n_windows}")
        print(f"Drawdown Events Found: {len(result_df)}")

    return result_df
