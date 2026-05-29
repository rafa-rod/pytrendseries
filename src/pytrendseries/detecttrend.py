import time
import warnings
from typing import Dict, Tuple, Union

import numpy as np
import pandas as pd
from numba import njit

warnings.filterwarnings("ignore")


def _treat_parameters(prices, trend="downtrend", limit=1, window=5):
    """Checking all parameters"""
    if not isinstance(limit, int):
        raise ValueError("Limit parameter must be a interger value.")
    if (not isinstance(window, int)) or (window < limit) or (window < 1):
        raise ValueError(
            "Window parameter must be a integer and greater than limit value (in days)."
        )
    if not isinstance(trend, str) or trend.lower() not in ["uptrend", "downtrend"]:
        raise ValueError(
            "Trend parameter must be string. Choose only 'uptrend' or 'downtrend'."
        )
    if (
        not isinstance(prices, pd.core.frame.DataFrame)
        or prices.empty
        or prices.shape[1] > 1
    ):
        raise ValueError(
            "Input must be a dataframe containing one column and its index must be in datetime format."
        )


@njit(cache=True)
def _scan(
    prices: np.ndarray,
    n: int,
    is_down: bool,
    limit: int,
    window: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Scan a price series and locate every trend within the given window.

    Walks the series sequentially and, for each starting point that begins a
    trend, finds the peak and valley that bound it. The peak and valley are
    each returned twice: once as the index used for the ``index_peak`` /
    ``index_valley`` columns (first occurrence of the extreme price) and once
    as the index used for the date columns (last occurrence of the extreme
    price), which may differ when prices are tied.

    Parameters
    ----------
    prices : np.ndarray
        One-dimensional ``float64`` array of observed prices, sorted by date.
    n : int
        Number of observations in ``prices``.
    is_down : bool
        ``True`` to detect downtrends, ``False`` to detect uptrends.
    limit : int
        Minimum number of periods between peak and valley for a trend to count.
    window : int
        Maximum number of periods a trend may span.

    Returns
    -------
    tuple of np.ndarray
        Six arrays of equal length, one entry per detected trend:
        ``(index_peak, index_valley, date_peak, date_valley, peak_price,
        valley_price)``.
    """
    from_idx = np.empty(n, dtype=np.int64)
    to_idx = np.empty(n, dtype=np.int64)
    from_didx = np.empty(n, dtype=np.int64)
    to_didx = np.empty(n, dtype=np.int64)
    peak_p = np.empty(n, dtype=np.float64)
    valley_p = np.empty(n, dtype=np.float64)
    count = 0

    i = 0
    while i < n - 1:
        price2 = prices[i]
        price1 = prices[i + 1]
        go = (is_down and price1 < price2) or ((not is_down) and price1 > price2)

        if go:
            end = i + window
            if end > n:
                end = n

            brk = -1
            for j in range(i, end):
                if (is_down and prices[j] > price2) or (
                    (not is_down) and prices[j] < price2
                ):
                    brk = j
                    break

            if brk != -1:
                seg_lo, seg_hi = i, brk
            else:
                seg_lo, seg_hi = i, end

            pmax = prices[seg_lo]
            for j in range(seg_lo, seg_hi):
                if is_down:
                    if prices[j] > pmax:
                        pmax = prices[j]
                else:
                    if prices[j] < pmax:
                        pmax = prices[j]
            loc_max = seg_lo
            for j in range(seg_lo, seg_hi):
                if prices[j] == pmax:
                    loc_max = j
                    break

            if brk != -1:
                f_lo = loc_max + 1
                f_hi = seg_hi
                if f_lo >= f_hi:
                    f_lo, f_hi = seg_lo, seg_hi
                pmin = prices[f_lo]
                for j in range(f_lo, f_hi):
                    if is_down:
                        if prices[j] < pmin:
                            pmin = prices[j]
                    else:
                        if prices[j] > pmin:
                            pmin = prices[j]
                loc_min = f_lo
                for j in range(f_lo, f_hi):
                    if prices[j] == pmin:
                        loc_min = j
                        break
                date_min = f_lo
                for j in range(f_lo, f_hi):
                    if prices[j] == pmin:
                        date_min = j
                date_max = loc_max
            else:
                pmin = prices[seg_lo]
                for j in range(seg_lo, seg_hi):
                    if is_down:
                        if prices[j] < pmin:
                            pmin = prices[j]
                    else:
                        if prices[j] > pmin:
                            pmin = prices[j]
                loc_min = seg_lo
                for j in range(seg_lo, seg_hi):
                    if prices[j] == pmin:
                        loc_min = j
                        break
                date_max = seg_lo
                for j in range(seg_lo, seg_hi):
                    if prices[j] == pmax:
                        date_max = j
                date_min = seg_lo
                for j in range(seg_lo, seg_hi):
                    if prices[j] == pmin:
                        date_min = j

            if loc_min - loc_max >= limit:
                from_idx[count] = loc_max
                to_idx[count] = loc_min
                from_didx[count] = date_max
                to_didx[count] = date_min
                peak_p[count] = pmax
                valley_p[count] = pmin
                count += 1
                i = loc_min - 1
        i += 1

    return (
        from_idx[:count],
        to_idx[:count],
        from_didx[:count],
        to_didx[:count],
        peak_p[:count],
        valley_p[:count],
    )


def detecttrend(
    df_prices: pd.DataFrame,
    trend: str = "downtrend",
    limit: int = 5,
    window: int = 21,
    **kwargs,
) -> pd.DataFrame:
    """Detect every up- or downtrend in a time series.

    Parameters
    ----------
    df_prices : pd.DataFrame
        Single-column DataFrame of prices indexed by date. A non-datetime index
        is converted with :func:`pandas.to_datetime`.
    trend : str, optional
        Either ``"downtrend"`` (default) or ``"uptrend"``.
    limit : int, optional
        Minimum number of periods between peak and valley for a trend to count.
        Defaults to ``5``.
    window : int, optional
        Maximum number of periods a trend may span. Defaults to ``21``.
    **kwargs
        Passed through to :func:`pandas.to_datetime`; ``format`` is honoured
        when converting a non-datetime index.

    Returns
    -------
    pd.DataFrame
        One row per detected trend. For a downtrend the columns are
        ``["Peak Date", "Valley Date", "Peak", "Valley", "index_peak",
        "index_valley", "time_span", "drawdown"]``; for an uptrend the peak and
        valley roles are swapped and the last column is ``"drawup"``. Rows are
        sorted by the first column.
    """
    if not pd.api.types.is_datetime64_ns_dtype(df_prices.index.dtype):
        df_prices.index = pd.to_datetime(df_prices.index, format=kwargs.get("format"))

    _treat_parameters(df_prices, trend, limit, window)

    df_prices = df_prices.sort_index()
    prices: np.ndarray = np.ascontiguousarray(
        df_prices.iloc[:, 0].values, dtype=np.float64
    )
    dates: np.ndarray = df_prices.index.values
    n: int = prices.shape[0]
    is_down: bool = trend.lower() == "downtrend"

    start: float = time.time()
    f_idx, t_idx, f_didx, t_didx, pk, vl = _scan(
        prices, n, is_down, int(limit), int(window)
    )

    time_span: np.ndarray = t_idx - f_idx
    if is_down:
        dd: np.ndarray = np.abs(pk - vl) / np.maximum(pk, vl)
        out: pd.DataFrame = pd.DataFrame(
            {
                "Peak Date": dates[f_didx],
                "Valley Date": dates[t_didx],
                "Peak": pk,
                "Valley": vl,
                "index_peak": f_idx,
                "index_valley": t_idx,
                "time_span": time_span,
                "drawdown": dd,
            }
        )
    else:
        mn: np.ndarray = np.minimum(pk, vl)
        with np.errstate(divide="ignore"):
            du: np.ndarray = np.where(mn == 0, np.inf, np.abs(pk - vl) / mn)
        out = pd.DataFrame(
            {
                "Valley Date": dates[f_didx],
                "Peak Date": dates[t_didx],
                "Valley": pk,
                "Peak": vl,
                "index_valley": f_idx,
                "index_peak": t_idx,
                "time_span": time_span,
                "drawup": du,
            }
        )

    out = out[out["time_span"] > 0]
    print("Trends detected in {} secs".format(round(time.time() - start, 4)))
    return out.sort_values(out.columns[0]).reset_index(drop=True)


def get_trends_labels(
    df: pd.DataFrame,
    labels: Dict[str, Union[int, float, str]] = None,
    window: int = 252,
    limit: int = 5,
) -> pd.DataFrame:
    """
    Adds a 'label' column to the dataframe based on detected trends.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with DatetimeIndex and 'Close' column.
    labels : Dict[str, Union[int, float, str]], optional
        Dictionary defining which trends to calculate and their values.
        Example: {"uptrend": 1, "downtrend": -1, "notrend": 0}
        Default: {"uptrend": 1, "downtrend": -1, "notrend": 0}
    window : int, optional
        Window for trend detection. Default: 252
    limit : int, optional
        Limit for trend detection. Default: 5

    Returns
    -------
    pd.DataFrame
        Dataframe with the new 'label' column added.

    Examples
    --------
    >>> df_labeled = get_trends_labels(df)
    >>> df_only_up = get_trends_labels(df, labels={"uptrend": 1, "notrend": 0})
    >>> df_custom = get_trends_labels(df, labels={"uptrend": "BUY", "downtrend": "SELL"})
    """

    if labels is None:
        labels = {"uptrend": 1, "downtrend": -1, "notrend": 0}

    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    default_label: Union[int, float, str] = labels.get("notrend", 0)
    df_labels = pd.DataFrame(index=df.index)

    if "uptrend" in labels:
        try:
            uptrends: pd.DataFrame = detecttrend(
                df,
                trend="uptrend",
                window=window,
                limit=limit,
            )

            if not uptrends.empty:
                uptrend_label: Union[int, float, str] = labels["uptrend"]

                for _, row in uptrends.iterrows():
                    start_date: pd.Timestamp = row["Valley Date"]
                    end_date: pd.Timestamp = row["Peak Date"]

                    mask: pd.Series = (df.index >= start_date) & (df.index <= end_date)

                    df_labels.loc[mask, "label"] = uptrend_label

        except Exception as e:
            print(f"Warning: Error processing uptrends: {e}")

    if "downtrend" in labels:
        try:
            downtrends: pd.DataFrame = detecttrend(
                df,
                trend="downtrend",
                window=window,
                limit=limit,
            )

            if not downtrends.empty:
                downtrend_label: Union[int, float, str] = labels["downtrend"]

                for _, row in downtrends.iterrows():
                    start_date: pd.Timestamp = row["Peak Date"]
                    end_date: pd.Timestamp = row["Valley Date"]

                    mask: pd.Series = (df.index >= start_date) & (df.index <= end_date)

                    df_labels.loc[mask, "label"] = downtrend_label

        except Exception as e:
            print(f"Warning: Error processing downtrends: {e}")

    df = pd.concat([df, df_labels], axis=1).fillna(default_label)
    return df
