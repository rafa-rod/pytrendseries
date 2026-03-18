#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 21:29:38 2021

@author: Rafael
"""

import time
import warnings
from typing import Dict, List, Union

import detecttrend
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


def calculate_time_under_water(
    df_prices: Union[pd.DataFrame, pd.Series], verbose: bool = True, **kwargs
) -> pd.DataFrame:
    """
    Calculates Time Under Water (TUW) - the period required to recover from drawdown.

    Time Under Water measures the number of periods from when the price first drops
    below a peak until it recovers to (or exceeds) that peak level.

    Parameters:
    -----------
    df_prices : Union[pd.DataFrame, pd.Series]
        Time series of prices. Must have a datetime index.
        If DataFrame, the first column is used.
    verbose : bool
        If True, prints execution time and summary statistics.
    **kwargs : dict
        Additional arguments (e.g., 'format' for datetime parsing if needed).

    Returns:
    --------
    pd.DataFrame
        DataFrame containing all drawdown periods with their recovery time.
        Columns: Peak Date, Recovery Date, Peak, Valley, MaxDD, Time Underwater, Status
    """
    detecttrend._treat_parameters(df_prices, trend="downtrend", limit=1, window=1)

    start_time = time.time()

    # 1. Validate and Prepare Index
    if not pd.api.types.is_datetime64_any_dtype(df_prices.index):
        df_prices.index = pd.to_datetime(df_prices.index, format=kwargs.get("format"))

    # Normalize input to Series
    if isinstance(df_prices, pd.DataFrame):
        price_series = df_prices.iloc[:, 0]
    else:
        price_series = df_prices

    if len(price_series) < 2:
        return pd.DataFrame(
            columns=[
                "Peak Date",
                "Recovery Date",
                "Peak",
                "Valley",
                "MaxDD",
                "Time Underwater",
                "Status",
            ]
        )

    # 2. Vectorized Calculation
    prices = price_series.to_numpy()
    dates = price_series.index.to_numpy()
    n = len(prices)

    # Calculate running maximum (peak) at each point
    running_peak = np.maximum.accumulate(prices)

    # Calculate drawdown at each point
    drawdown = (prices / running_peak) - 1

    # 3. Identify underwater periods (drawdown < 0 means price is below running peak)
    underwater = drawdown < -1e-10  # Small epsilon to avoid floating point issues

    # 4. Find contiguous underwater periods using diff
    underwater_int = underwater.astype(int)
    diff = np.diff(underwater_int, prepend=0, append=0)

    # Start of underwater periods (0 -> 1 transition)
    underwater_starts = np.where(diff == 1)[0]
    # End of underwater periods (1 -> 0 transition)
    underwater_ends = np.where(diff == -1)[0]

    # Ensure equal length (handle case where series ends while underwater)
    if len(underwater_starts) > len(underwater_ends):
        underwater_ends = np.append(underwater_ends, n)

    results: List[Dict] = []

    # 5. Process each distinct underwater period
    for start_idx, end_idx in zip(underwater_starts, underwater_ends):
        # Find the peak that preceded this underwater period
        # Look at running peak just before going underwater
        peak_idx = start_idx - 1
        if peak_idx < 0:
            continue

        peak_value = running_peak[peak_idx]
        peak_date = dates[peak_idx]

        # Find the actual peak date (when this peak value was first reached)
        # Search backwards for when running_peak first equals peak_value
        peak_first_idx = np.argmax(running_peak[: peak_idx + 1] == peak_value)
        peak_date = dates[peak_first_idx]

        # Get prices during underwater period
        underwater_prices = prices[start_idx:end_idx]
        underwater_dates = dates[start_idx:end_idx]

        if len(underwater_prices) == 0:
            continue

        # Find valley (minimum) during this underwater period
        valley_idx_in_period = np.argmin(underwater_prices)
        valley_value = underwater_prices[valley_idx_in_period]
        valley_date = underwater_dates[valley_idx_in_period]

        # Determine recovery date and status
        if end_idx < n:
            # Recovered - price came back above peak
            recovery_date = dates[end_idx - 1]
            status = "Recovered"
            time_underwater = int(end_idx - start_idx)
        else:
            # Still underwater at end of series
            recovery_date = pd.NaT
            status = "Ongoing"
            time_underwater = int(n - start_idx)

        # Ensure time_underwater is never negative
        time_underwater = max(1, time_underwater)

        # Calculate maximum drawdown for this period
        maxdd = abs((valley_value / peak_value) - 1)

        results.append(
            {
                "Peak Date": pd.Timestamp(peak_date),
                "Recovery Date": pd.Timestamp(recovery_date)
                if status == "Recovered"
                else pd.NaT,
                "Peak": float(peak_value),
                "Valley": float(valley_value),
                "MaxDD": float(maxdd),
                "Time Underwater": time_underwater,
                "Status": status,
            }
        )

    # 6. Build Result DataFrame
    if results:
        result_df = pd.DataFrame(results)
        result_df = result_df.sort_values("MaxDD", ascending=False).reset_index(
            drop=True
        )
    else:
        result_df = pd.DataFrame(
            columns=[
                "Peak Date",
                "Recovery Date",
                "Peak",
                "Valley",
                "MaxDD",
                "Time Underwater",
                "Status",
            ]
        )

    if verbose:
        elapsed_time = time.time() - start_time
        n_recovered = len(result_df[result_df["Status"] == "Recovered"])
        n_ongoing = len(result_df[result_df["Status"] == "Ongoing"])
        print(f"TUW calculated in {elapsed_time:.3f} seconds")
        print(f"Total drawdown periods: {len(result_df)}")
        print(f"  - Recovered: {n_recovered}")
        print(f"  - Ongoing: {n_ongoing}")

    return result_df
